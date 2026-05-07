import express from 'express';
import { config } from './config/index.js';
import { createRepositories } from './repositories/index.js';
import { PasswordHasher } from './services/PasswordHasher.js';
import { TokenService } from './services/TokenService.js';
import { AuthService } from './services/AuthService.js';
import { buildRoutes } from './routes/index.js';
import { errorHandler } from './middlewares/errorHandler.js';
import { notFound } from './middlewares/notFound.js';

/**
 * Cria a aplicação Express com todas as dependências montadas.
 * Aceita overrides para facilitar testes (ex.: substituir hasher ou tokens).
 */
export const createApp = (overrides = {}) => {
  const app = express();
  app.use(express.json({ limit: '1mb' }));

  const repos = overrides.repos || createRepositories();
  const hasher = overrides.hasher || new PasswordHasher({ rounds: config.bcrypt.rounds });
  const tokens = overrides.tokens || new TokenService({
    secret: config.jwt.secret,
    expiresIn: config.jwt.expiresIn,
    refreshSecret: config.jwt.refreshSecret,
    refreshExpiresIn: config.jwt.refreshExpiresIn
  });
  const authService = overrides.authService || new AuthService({ userRepo: repos.users, hasher, tokens });

  // Health check
  app.get('/health', (req, res) => res.json({ status: 'ok', env: config.env }));

  // API
  app.use('/api', buildRoutes({ authService, repos, hasher }));

  app.use(notFound);
  app.use(errorHandler);

  // Expor componentes para uso em testes/integração
  app.locals.authService = authService;
  app.locals.repos = repos;
  app.locals.hasher = hasher;
  app.locals.tokens = tokens;

  return app;
};

export default createApp;
