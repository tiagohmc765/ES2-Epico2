/**
 * Testes de unidade — middleware authenticate.
 * Mapeamento: TU-AUTH-15
 *
 * Técnica: Particionamento de Equivalência sobre o header Authorization.
 *   Classes:
 *     - Header em falta
 *     - Header sem esquema "Bearer"
 *     - Header com Bearer mas token vazio
 *     - Header válido com token aceite pelo authService
 *     - Header válido com token rejeitado pelo authService
 */
import { jest } from '@jest/globals';
import { authenticate } from '../../../src/middlewares/authenticate.js';
import { AuthError } from '../../../src/services/AuthService.js';

const mkRes = () => {
  const res = {};
  res.status = jest.fn().mockReturnValue(res);
  res.json = jest.fn().mockReturnValue(res);
  return res;
};

describe('[TU-AUTH-15] authenticate() middleware', () => {
  test('sem header Authorization → 401', () => {
    const next = jest.fn();
    const res = mkRes();
    authenticate({ authenticate: () => ({}) })({ headers: {} }, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  test('esquema diferente de Bearer → 401', () => {
    const next = jest.fn();
    const res = mkRes();
    authenticate({ authenticate: () => ({}) })(
      { headers: { authorization: 'Basic abc' } }, res, next
    );
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  test('Bearer sem token → 401', () => {
    const next = jest.fn();
    const res = mkRes();
    authenticate({ authenticate: () => ({}) })(
      { headers: { authorization: 'Bearer ' } }, res, next
    );
    expect(res.status).toHaveBeenCalledWith(401);
  });

  test('token aceite injeta req.user e chama next()', () => {
    const fakeUser = { id: 1, email: 'a@b.c', role: 'Tecnico' };
    const authService = { authenticate: jest.fn().mockReturnValue(fakeUser) };
    const next = jest.fn();
    const res = mkRes();
    const req = { headers: { authorization: 'Bearer abc.def.ghi' } };
    authenticate(authService)(req, res, next);
    expect(authService.authenticate).toHaveBeenCalledWith('abc.def.ghi');
    expect(req.user).toEqual(fakeUser);
    expect(next).toHaveBeenCalled();
  });

  test('token rejeitado pelo authService devolve status do AuthError', () => {
    const authService = {
      authenticate: () => { throw new AuthError('Invalid', 'INVALID_TOKEN', 401); }
    };
    const next = jest.fn();
    const res = mkRes();
    authenticate(authService)({ headers: { authorization: 'Bearer x' } }, res, next);
    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });
});
