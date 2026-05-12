import { Router } from 'express';
import { buildAuthRoutes } from './authRoutes.js';
import { buildUsersRoutes } from './usersRoutes.js';
import { buildResourceRoutes } from './resourceRoutes.js';
import { Roles } from '../domain/enums.js';

/**
 * Monta o conjunto completo de rotas, declarando perfis autorizados por recurso.
 *
 * Convenções (Sprint 1, esqueleto):
 *   - /auth                      público (login/register/refresh) + /me autenticado
 *   - /users                     Administrador
 *   - /herbs                     leitura: todos; escrita: Responsavel/Administrador
 *   - /plans                     leitura: todos; escrita: Responsavel/Administrador
 *   - /batches                   leitura: todos; escrita: Tecnico/Responsavel/Administrador
 *   - /tasks                     leitura: todos; escrita: Tecnico/Responsavel/Administrador
 *   - /measurements              leitura: todos; escrita: Tecnico
 *   - /alerts                    leitura: todos; escrita: Responsavel/Administrador
 *   - /automation                leitura: todos; escrita: Responsavel/Administrador
 *   - /reports                   leitura: Responsavel/Administrador
 *   - /audit                     leitura: Administrador
 */
export const buildRoutes = ({ authService, repos, hasher }) => {
  const router = Router();

  router.use('/auth', buildAuthRoutes(authService));
  router.use('/users', buildUsersRoutes({ authService, userRepo: repos.users, hasher, audit: repos.audit }));

  router.use('/herbs', buildResourceRoutes({
    resourceName: 'herbs', repo: repos.herbs, audit: repos.audit, authService,
    permissions: { write: [Roles.RESPONSAVEL, Roles.ADMINISTRADOR] }
  }));

  router.use('/plans', buildResourceRoutes({
    resourceName: 'plans', repo: repos.plans, audit: repos.audit, authService,
    permissions: { write: [Roles.RESPONSAVEL, Roles.ADMINISTRADOR] }
  }));

  router.use('/batches', buildResourceRoutes({
    resourceName: 'batches', repo: repos.batches, audit: repos.audit, authService,
    permissions: { write: [Roles.TECNICO, Roles.RESPONSAVEL, Roles.ADMINISTRADOR] }
  }));

  router.use('/tasks', buildResourceRoutes({
    resourceName: 'tasks', repo: repos.tasks, audit: repos.audit, authService,
    permissions: { write: [Roles.TECNICO, Roles.RESPONSAVEL, Roles.ADMINISTRADOR] }
  }));

  router.use('/measurements', buildResourceRoutes({
    resourceName: 'measurements', repo: repos.measurements, audit: repos.audit, authService,
    permissions: { write: [Roles.TECNICO] }
  }));

  router.use('/alerts', buildResourceRoutes({
    resourceName: 'alerts', repo: repos.alerts, audit: repos.audit, authService,
    permissions: { write: [Roles.RESPONSAVEL, Roles.ADMINISTRADOR] }
  }));

  router.use('/automation', buildResourceRoutes({
    resourceName: 'automation', repo: repos.automation, audit: repos.audit, authService,
    permissions: { write: [Roles.RESPONSAVEL, Roles.ADMINISTRADOR] }
  }));

  router.use('/reports', buildResourceRoutes({
    resourceName: 'reports', repo: repos.audit /* placeholder */, audit: repos.audit, authService,
    permissions: { read: [Roles.RESPONSAVEL, Roles.ADMINISTRADOR], write: [Roles.RESPONSAVEL, Roles.ADMINISTRADOR] }
  }));

  router.use('/audit', buildResourceRoutes({
    resourceName: 'audit', repo: repos.audit, audit: repos.audit, authService,
    permissions: { read: [Roles.ADMINISTRADOR], write: [Roles.ADMINISTRADOR] }
  }));

  return router;
};
