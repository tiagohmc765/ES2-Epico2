/**
 * Testes de unidade — middleware de autorização (RBAC).
 * Mapeamento: TU-AUTH-14
 *
 * Técnica: Particionamento de Equivalência sobre o perfil:
 *   - perfis dentro do conjunto autorizado → next() chamado
 *   - perfis fora do conjunto autorizado   → 403
 *   - sem req.user                         → 401
 */
import { jest } from '@jest/globals';
import { authorize } from '../../../src/middlewares/authorize.js';
import { Roles } from '../../../src/domain/enums.js';

const mkRes = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

describe('[TU-AUTH-14] authorize() middleware', () => {
  test('sem req.user → 401', () => {
    const next = jest.fn();
    const res = mkRes();
    authorize(Roles.ADMINISTRADOR)({}, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  test('perfil autorizado → next()', () => {
    const next = jest.fn();
    const res = mkRes();
    authorize(Roles.ADMINISTRADOR)({ user: { role: Roles.ADMINISTRADOR } }, res, next);
    expect(next).toHaveBeenCalled();
    expect(res.status).not.toHaveBeenCalled();
  });

  test('perfil não autorizado → 403', () => {
    const next = jest.fn();
    const res = mkRes();
    authorize(Roles.ADMINISTRADOR)({ user: { role: Roles.TECNICO } }, res, next);
    expect(res.status).toHaveBeenCalledWith(403);
    expect(next).not.toHaveBeenCalled();
  });

  test('lista vazia (qualquer autenticado) → next()', () => {
    const next = jest.fn();
    const res = mkRes();
    authorize()({ user: { role: Roles.TECNICO } }, res, next);
    expect(next).toHaveBeenCalled();
  });

  test.each([
    [Roles.TECNICO, [Roles.TECNICO, Roles.ADMINISTRADOR], true],
    [Roles.RESPONSAVEL, [Roles.TECNICO, Roles.ADMINISTRADOR], false],
    [Roles.ADMINISTRADOR, [Roles.TECNICO, Roles.ADMINISTRADOR], true]
  ])('perfil %s contra [%p] permite=%s', (role, allowed, ok) => {
    const next = jest.fn();
    const res = mkRes();
    authorize(...allowed)({ user: { role } }, res, next);
    if (ok) expect(next).toHaveBeenCalled();
    else expect(res.status).toHaveBeenCalledWith(403);
  });
});
