# GREENHERB — Gestão Inteligente de Estufa

Projeto Python (FastAPI + pytest) para a unidade curricular de Engenharia de Software II.

## Estrutura do projeto

```
greenherb/
  auth/           # Autenticação, JWT, controlo de acesso, gestão de utilizadores
  herbs/          # Catálogo de ervas aromáticas e importação CSV
  plans/          # Planos de cultivo (regular, emergência, pontual)
  app.py          # Registo de routers FastAPI
data/
  users.json      # Utilizadores persistidos
tests/
  unit/           # Testes unitários (auth, herbs, plans)
  integration/    # Testes de integração HTTP (auth, users)
docs/
  matriz_rastreabilidade.md   # Matriz de rastreabilidade completa (Sprint 1 e 2)
  tecnicas_teste.md           # PE, VL e MC/DC documentados
```

## Endpoints disponíveis

| Método | Endpoint | Descrição | Perfis |
|---|---|---|---|
| POST | `/auth/login` | Autenticação; devolve access + refresh token | — |
| POST | `/auth/refresh` | Renovação do access token | — |
| GET | `/users` | Listar utilizadores | ADMIN |
| POST | `/users` | Criar utilizador | ADMIN |
| GET | `/users/{id}` | Obter utilizador por id | ADMIN |
| DELETE | `/users/{id}` | Eliminar utilizador | ADMIN |
| GET | `/herbs` | Listar ervas aromáticas | todos |
| POST | `/herbs` | Criar erva aromática | ADMIN, RESPONSAVEL |
| GET | `/herbs/{id}` | Obter erva por id | todos |
| POST | `/herbs/import` | Importar ervas via CSV | ADMIN |
| GET | `/plans` | Listar planos de cultivo | todos |
| POST | `/plans` | Criar plano de cultivo | ADMIN, RESPONSAVEL |
| GET | `/plans/{id}` | Obter plano por id | todos |

## Instalar dependências

```bash
pip install -r requirements.txt
```

## Executar testes

```bash
pytest
```

Com relatório de cobertura detalhado:

```bash
pytest --cov=greenherb --cov-report=html
```

## Executar a API

```bash
uvicorn greenherb.app:app --reload
```

Swagger UI disponível em: `http://127.0.0.1:8000/docs`

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|---|---|---|
| `JWT_SECRET` | Segredo para assinatura dos tokens JWT | `segredo-super-secreto` (**não usar em produção**) |

## Utilizadores de exemplo

Os utilizadores pré-carregados estão em `data/users.json`:

| Email | Password | Perfil |
|---|---|---|
| `admin@greenherb.pt` | `Admin123!` | ADMIN |
| `tecnico@greenherb.pt` | `Tecnico123!` | TECNICO |
| `responsavel@greenherb.pt` | `Responsavel123!` | RESPONSAVEL |

Exemplo de login:

```json
POST /auth/login
{
  "email": "admin@greenherb.pt",
  "password": "Admin123!"
}
```

## Exemplo de importação CSV

```json
POST /herbs/import
Authorization: Bearer <token>
{
  "content": "name,family,scientific_name\nBasil,Lamiaceae,Ocimum basilicum\nRosemary,Lamiaceae,Salvia rosmarinus"
}
```

## Exemplo de criação de plano pontual

```json
POST /plans
Authorization: Bearer <token>
{
  "type": "pontual",
  "herb_id": 1,
  "temp_min": 18.0,
  "temp_max": 28.0,
  "humidity_min": 40.0,
  "humidity_max": 80.0,
  "luminosity_min": 5000.0,
  "luminosity_max": 25000.0,
  "cycle_days": 90,
  "authorized_by": 3
}
```

## Estado dos sprints

| Sprint | Testes | Cobertura |
|---|---|---|
| Sprint 1 — Autenticação e utilizadores | 59 testes (31 unidade + 23 integração + 5 VL) | 100% |
| Sprint 2 — Ervas (importação CSV) e planos de cultivo | 48 testes (13 PE herbs + 35 PE/VL/MC-DC plans) | 100% lógica de domínio |

