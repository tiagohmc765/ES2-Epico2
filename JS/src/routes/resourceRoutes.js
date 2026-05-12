import { Router } from 'express';
import { buildGenericController } from '../controllers/genericController.js';
import { authenticate } from '../middlewares/authenticate.js';
import { authorize } from '../middlewares/authorize.js';

/**
 * Cria um router CRUD genérico para um recurso, com auth + RBAC.
 *
 * @param {object} opts
 * @param {string} opts.resourceName  Nome lógico (ex.: 'herbs')
 * @param {object} opts.repo          Repositório do recurso
 * @param {object} opts.audit         AuditRepo
 * @param {object} opts.authService   Serviço de autenticação
 * @param {object} [opts.permissions] Mapa { read?: [], write?: [] } com perfis autorizados.
 *                                    Se omitido, qualquer utilizador autenticado.
 */
export const buildResourceRoutes = ({ resourceName, repo, audit, authService, permissions = {} }) => {
  const router = Router();
  const c = buildGenericController({ repo, resourceName, audit });

  router.use(authenticate(authService));

  const readGuard = permissions.read?.length
    ? authorize(...permissions.read)
    : (req, res, next) => next();
  const writeGuard = permissions.write?.length
    ? authorize(...permissions.write)
    : (req, res, next) => next();

  router.get('/', readGuard, c.list);
  router.get('/:id', readGuard, c.get);
  router.post('/', writeGuard, c.create);
  router.patch('/:id', writeGuard, c.update);
  router.delete('/:id', writeGuard, c.remove);
  return router;
};
