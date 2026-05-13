# GREENHERB - Gestao Inteligente de Estufa

Projeto em Python com FastAPI para autenticacao, gestao de utilizadores, ervas aromaticas e planos de cultivo.

## Tecnologias

- Python
- FastAPI
- Uvicorn
- Pytest + pytest-cov

## Estrutura do projeto

```
greenherb/
  app.py                # Registo dos routers FastAPI
  auth/                 # Login, refresh token, ACL e gestao de utilizadores
  herbs/                # CRUD de ervas e importacao CSV
  plans/                # CRUD de planos e validacoes de negocio
data/
  users.json            # Utilizadores persistidos
docs/
  matriz_rastreabilidade.xlsx
  tecnicas_teste.md
tests/
  unit/
  integration/
```

## Como executar localmente

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Arrancar a API:

```bash
uvicorn greenherb.app:app --reload
```

3. Abrir documentacao interativa:

- Swagger UI: http://127.0.0.1:8000/docs

## Testes

Executar todos os testes:

```bash
pytest
```

Executar com cobertura HTML:

```bash
pytest --cov=greenherb --cov-report=html
```

## Endpoints principais

### Autenticacao

- POST /auth/login
- POST /auth/refresh

### Utilizadores (ADMIN)

- GET /users
- POST /users
- GET /users/{user_id}
- DELETE /users/{user_id}

### Ervas

- GET /herbs (ADMIN, RESPONSAVEL, TECNICO)
- POST /herbs (ADMIN, RESPONSAVEL)
- GET /herbs/{herb_id} (ADMIN, RESPONSAVEL, TECNICO)
- POST /herbs/import (ADMIN)

### Planos

- GET /plans (ADMIN, RESPONSAVEL, TECNICO)
- POST /plans (ADMIN, RESPONSAVEL)
- GET /plans/{plan_id} (ADMIN, RESPONSAVEL, TECNICO)

## Variaveis de ambiente

| Variavel | Descricao | Valor por omissao |
|---|---|---|
| JWT_SECRET | Segredo para assinatura de JWT | segredo-super-secreto |

Nota: o valor por omissao e apenas para desenvolvimento.

## Exemplo rapido de autenticacao

Pedido:

```json
POST /auth/login
{
  "email": "admin@greenherb.pt",
  "password": "Admin123!"
}
```

Depois de autenticar, enviar o token no header Authorization:

```text
Authorization: Bearer <access_token>
```

