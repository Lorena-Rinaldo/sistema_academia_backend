<h1 align="center">🏋️ Sistema Academia Backend API ✨</h1>

Bem-vindo ao **Sistema de Gerenciamento de Academia**! Uma API RESTful robusta desenvolvida em Flask para controle completo de alunos, com autenticação JWT segura, integração com Firebase Firestore e documentação OpenAPI interativa. Gerencie cadastros, status de acesso (ativo/inativo) e consultas públicas por CPF!

## Índice

*   [Sobre o Projeto](#sobre-o-projeto)
*   [Tecnologias Utilizadas](#tecnologias-utilizadas)
*   [Funcionalidades Implementadas](#funcionalidades-implementadas)
*   [Como Executar o Projeto Localmente](#como-executar-o-projeto-localmente)
*   [Estrutura do Projeto](#estrutura-do-projeto)
*   [Contato](#contato)

## Sobre o Projeto

O objetivo principal deste projeto é fornecer uma API backend completa para academias, permitindo o CRUD de alunos com validação rigorosa de CPF brasileiro, controle de status (ativo/inativo) para liberação de acesso, autenticação admin via JWT e consultas públicas para verificação de acesso. 
O foco está na robustez, segurança (tokens JWT), escalabilidade com Firebase Firestore e documentação automática via Flasgger/OpenAPI para fácil integração frontend/mobile.

## Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias Python/Backend:

*   **Flask:**
    * Framework web leve e poderoso para as rotas RESTful.
*   **Firebase Admin/Firestore:**
    * Banco NoSQL serverless para armazenamento de alunos e contador de IDs.
*   **Flasgger/OpenAPI:**
    * Geração automática de documentação Swagger interativa (openapi.yaml).
*   **PyJWT:**
    * Autenticação stateless com tokens Bearer (expiração 1h).
*   **validate-docbr:**
    * Validação oficial de CPF brasileiro.
*   **Flask-CORS/python-dotenv:**
    * Suporte CORS para frontends e carregamento de variáveis de ambiente (.env).

## Funcionalidades Implementadas

*   **Autenticação Admin Segura:**
    * POST /login → Token JWT para acesso às rotas privadas.
    * Decorator @token_obrigatorio em todas operações CRUD.
*   **CRUD Completo de Alunos:**
    * POST /alunos: Criar com ID auto-incremental, valida CPF único/BR.
    * GET /alunos: Lista paginada (limite query param).
    * PUT /alunos/{cpf}: Update completo.
    * PATCH /alunos/{cpf}: Update parcial (flexível).
    * DELETE /alunos/{cpf}: Remoção segura.
*   **Consulta Pública de Acesso:**
    * GET /alunos/{cpf}: Verifica status e libera mensagem (BEM-VINDO! / ACESSO NEGADO).
*   **Validações e Erros:**
    * CPF válido BR, status enum (ativo/inativo), duplicatas 409, autenticação 401, etc.
    * Handlers de erro 404/500.
*   **Documentação Interativa:**
    * http://localhost:5000/apidocs → Swagger UI automático.

## Como Executar o Projeto Localmente

Para rodar a API localmente:

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure variáveis de ambiente (.env):**
    ```
    SECRET_KEY=sua_chave_secreta
    ADM_USUARIO=admin
    ADM_SENHA=123456
    FIREBASE_CREDENTIALS='{"type":"service_account",...}'  # Ou firebase.json local
    ```

3.  **Execute a API:**
    ```bash
    python app.py
    ```

4.  **Acesse:**
    * API: http://localhost:5000
    * Docs: http://localhost:5000/apidocs

Para deploy Vercel: Defina FIREBASE_CREDENTIALS como env var JSON.

## Estrutura do Projeto

```
.
├── app.py                 # API Flask principal (rotas, lógica, Firestore)
├── auth.py                # JWT: gerar_token() e @token_obrigatorio decorator
├── openapi.yaml           # Especificação OpenAPI 3.0 para Flasgger/Swagger
├── requirements.txt       # Dependências Python
├── firebase.json          # Credenciais Firebase (gitignore)
├── .env                   # Vars de ambiente (gitignore)
├── .gitignore
└── README.md
```

## Contato

Desenvolvido por: **Lorena Rinaldo e Isabelly Lima**

*   **Lorena Rinaldo**: https://github.com/Lorena-Rinaldo
*   **Isabelly Lima**: https://github.com/isabelly-lima05


---

🏋️ Gerencie sua academia com eficiência e segurança! ✨
