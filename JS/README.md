# GREENHERB - ES2 Épico 2

Plataforma de Gestão Inteligente de Estufa de Ervas Aromáticas — API REST em Node.js/Express.

## Estrutura do Projeto

```
src/
  config/         Configuração e variáveis de ambiente
  domain/         Modelos de domínio e enumerações
  repositories/   Repositórios in-memory (abstração de persistência)
  services/       Lógica de negócio (AuthService, etc.)
  middlewares/    Autenticação, autorização (RBAC), validação, erros
  controllers/    Manipuladores HTTP por recurso
  routes/         Definição de rotas Express
  app.js          Aplicação Express configurada
  index.js        Bootstrap do servidor
tests/
  unit/           Testes de unidade (Sprint 1: foco em /auth)
  helpers/        Factories e fixtures para testes
docs/
  matriz-rastreabilidade.xlsx
  relatorio-sprint1.docx
```

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

## Testes

```bash
npm test                   # Corre toda a bateria
npm run test:auth          # Apenas testes de autenticação
npm run test:coverage      # Com relatório de cobertura
```

## Sprint 1 — Entregáveis

1. Endpoints REST em Node.js (esqueleto de todos os recursos da API)
2. Testes de unidade da autenticação (Particionamento de Equivalência, Valores Limite, MC/DC)
3. Matriz de rastreabilidade inicial e relatório

## Perfis de Utilizador

- **Tecnico** — operações de campo (medições, tarefas)
- **Responsavel** — gestão de planos e aprovação de planos pontuais
- **Administrador** — gestão de utilizadores e configuração geral
