import { Router } from 'express';
import { buildAuthController } from '../controllers/authController.js';
import { authenticate } from '../middlewares/authenticate.js';

export const buildAuthRoutes = (authService) => {
  const router = Router();
  const c = buildAuthController(authService);
  router.post('/register', c.register);
  router.post('/login', c.login);
  router.post('/refresh', c.refresh);
  router.get('/me', authenticate(authService), c.me);
  return router;
};
