from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import json
from auth import token_obrigatorio, gerar_token
from flask_cors import CORS
from flasgger import Swagger
from validate_docbr import CPF

load_dotenv()

if os.getenv("VERCEL"):
    # online na vercel
    cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
else:
    # localmente
    cred = credentials.Certificate("firebase.json")

# Carrega as credenciais do Firebase localmente
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

# VERSÃO DA OPENAPI
app.config["SWAGGER"] = {"openapi": "3.0.0"}

# CHAMAR O OPENAPI PARA O CÓDIGO
swagger = Swagger(app, template_file="openapi.yaml")

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
CORS(app, origins="*")
ADM_USUARIO = os.getenv("ADM_USUARIO")
ADM_SENHA = os.getenv("ADM_SENHA")

# ----- FUNÇÕES -----
def validar_cpf_real(numero_cpf):
    cpf = CPF()
    return cpf.validate(numero_cpf)

# ----- MÉTODOS PÚBLICOS -----

# Rota PRINCIPAL - Apresentação da API
@app.route("/", methods=["GET"])
def root():
    return jsonify(
        {
            "api": "academia",
            "version": "1.0",
            "author": "Lorena Rinaldo e Isabelly Lima",
        }
    )


# Rota LOGIN
@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Envie os dados para login"}), 400

    usuario = dados.get("usuario")
    senha = dados.get("senha")

    if not usuario or not senha:
        return jsonify({"error": "Usuário e senha são obrigatórios!!"}), 400

    if usuario == ADM_USUARIO and senha == ADM_SENHA:
        token = gerar_token(usuario)
        return jsonify({"message": "Login realizado com sucesso", "token": token}), 200

    return jsonify({"error": "Usuário e/ou senha inválidos"}), 401

# ----- MÉTODOS PÚBLICOS -----

# Rota 1 - Método GET - Retorna aluno pelo cpf
@app.route("/alunos/<string:cpf>", methods=["GET"])
def get_aluno(cpf):
    docs = db.collection("alunos").where("cpf", "==", cpf).limit(1).get()
    
    if not docs:
        return jsonify({"error": "Aluno não encontrado"}), 404
    
    aluno = docs[0].to_dict()

    acesso_liberado = aluno.get("status", False)
    
    return jsonify({
        "nome": aluno.get("nome"),
        "status": aluno.get("status"),
        "liberado": acesso_liberado,
        "mensagem": "BEM-VINDO(A)!" if acesso_liberado else "ACESSO NEGADO"
    }), 200


# ----- MÉTODOS PRIVADOS -----

# Rota 1 - Método GET - Todas os usuários
@app.route("/alunos", methods=["GET"])
@token_obrigatorio
def get_alunos():
    # Padrão limite de 50
    limite = request.args.get("limite", default=50, type=int)

    alunos = []  # Lista vazia

    lista = (
        db.collection("alunos").limit(limite).stream()
    )  # stream lista todos os dados

    # Tranforma objeto do firestore em dicionário python
    for item in lista:
        alunos.append(item.to_dict())
    return jsonify(alunos), 200

# Rota 2 - Método POST - Cadastro de novo aluno
@app.route("/alunos", methods=["POST"])
@token_obrigatorio
def post_alunos():
    dados = request.get_json()
    
    if not dados or "cpf" not in dados or "nome" not in dados:
        return jsonify({"error": "Dados inválidos ou incompletos"}), 400
    
    status = dados.get("status")
    if not isinstance(status, bool):
        status = True
    
    cpf = dados["cpf"]
    
    if not validar_cpf_real(cpf):
        return jsonify({"error": "O CPF informado é inválido!"}), 400

    try:
        # Verifica se o CPF já está cadastrado
        aluno_existente = db.collection("alunos").where("cpf", "==", cpf).limit(1).get()

        if aluno_existente:
            return jsonify({"error": "Este CPF já está cadastrado no sistema!"}), 409
        
        # Busca pelo contador de id
        contador_ref = db.collection("contador").document("controle_id")
        contador_doc = contador_ref.get()
        ultimo_id = contador_doc.to_dict().get("ultimo_id")

        # Somar 1 ao último id
        novo_id = ultimo_id + 1

        # Atualiza o id do contador do firebase
        contador_ref.update({"ultimo_id": novo_id})

        # Cadastrar novo aluno
        db.collection("alunos").add(
            {
                "id": novo_id,
                "cpf": dados["cpf"],
                "nome": dados["nome"],
                "status": status
            }
        )

        return jsonify({"message": "Aluno(a)criado(a) com sucesso!"}), 201

    except:
        return jsonify({"error": "Falha no envio do arquivo"}), 400


# Rota 3 - Método PUT - Alteração total
@app.route("/alunos/<string:cpf>", methods=["PUT"])
@token_obrigatorio
def alunos_put(cpf):

    dados = request.get_json()

    # PUT - É necessário enviar valores
    if not dados or "cpf" not in dados or "status" not in dados or "nome" not in dados:
        return jsonify({"error": "Dados inválidos ou incompletos"}), 400

    try:
        docs = db.collection("alunos").where("cpf", "==", cpf).limit(1).get()
        if not docs:
            return jsonify({"error": "Aluno(a) não encontrado(a)"}), 404

        # Pega o primeiro (e único) documento da lista
        for doc in docs:
            doc_ref = db.collection("alunos").document(doc.id)

            doc_ref.update(
                {"cpf": dados["cpf"], "nome": dados["nome"], "status": dados["status"]}
            )

        return (jsonify({"message": "Aluno(a) alterado(a) com sucesso!"}), 200)
    except:
        return jsonify({"error": "Dados inválidos ou incompletos"}), 400


# Rota 4 - Método PATCH - Alteração parcial (status)
@app.route("/alunos/<string:cpf>", methods=["PATCH"])
@token_obrigatorio
def alunos_patch(cpf):

    dados = request.get_json()

    # PATCH - Pode ter SÓ UM dos dados
    if not dados:
        return jsonify({"error": "Dados inválidos!"}), 400

    try:
        docs = db.collection("alunos").where("cpf", "==", cpf).limit(1).get()
        if not docs:
            return jsonify({"error": "Aluno(a) não encontrado(a)"}), 404

        doc_ref = db.collection("alunos").document(docs[0].id)

        update_aluno = {}

        if "cpf" in dados:
            update_aluno["cpf"] = dados["cpf"]
        if "nome" in dados:
            update_aluno["nome"] = dados["nome"]
        if "status" in dados:
            update_aluno["status"] = dados["status"]    

        # Atualiza o Firestore
        doc_ref.update(update_aluno)

        return (jsonify({"message": "Aluno(a) alterado(a) com sucesso!"}), 200)
    except:
        return jsonify({"error": "Dados inválidos ou incompletos"}), 400


# Rota 5 - Método DELETE - Deletar aluno
@app.route("/alunos/<string:cpf>", methods=["DELETE"])
@token_obrigatorio
def alunos_delete(cpf):

    docs = db.collection("alunos").where("cpf", "==", cpf).limit(1).get()

    if not docs:
        return jsonify({"error": "Aluno(a) não encontrado(a)"}), 404

    doc_ref = db.collection("alunos").document(docs[0].id)
    doc_ref.delete()

    return (jsonify({"message": "Aluno(a) deletado(a) com sucesso!"}), 200)


# ----- ROTAS DE TRATAMENTO DE ERRO -----


@app.errorhandler(404)
def error404(error):
    return jsonify({"error": "URL não encontrada"}), 404


@app.errorhandler(500)
def error500(error):
    return jsonify({"error": "Servidor interno com falhas. Tente mais tarde!"}), 500


if __name__ == "__main__":
    app.run(debug=True)
