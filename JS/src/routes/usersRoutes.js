import { Router } from 'express';
import { buildUsersController } from '../controllers/usersController.js';
import { authenticate } from '../middlewares/authenticate.js';
import { authorize } from '../middlewares/authorize.js';
import { Roles } from '../domain/enums.js';

export const buildUsersRoutes = ({ authService, userRepo, hasher, audit }) => {
  const router = Router();
  const c = buildUsersController({ userRepo, hasher, audit });
  // Todas as rotas requerem autenticação
  router.use(authenticate(authService));
  // CRUD de utilizadores: apenas Administrador
  router.get('/', authorize(Roles.ADMINISTRADOR), c.list);
  router.get('/:id', authorize(Roles.ADMINISTRADOR), c.getById);
  router.post('/', authorize(Roles.ADMINISTRADOR), c.create);
  router.patch('/:id', authorize(Roles.ADMINISTRADOR), c.update);
  router.delete('/:id', authorize(Roles.ADMINISTRADOR), c.remove);
  return router;
};
