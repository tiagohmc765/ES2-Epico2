/**
 * Testes de unidade — TokenService (wrapper sobre jsonwebtoken).
 * Mapeamento: TU-AUTH-07, TU-AUTH-08
 *
 * Técnicas:
 *   - Particionamento de Equivalência (token válido / inválido / expirado / com segredo errado)
 *   - Valores Limite (expiração: imediatamente antes/depois)
 */
import { TokenService } from '../../../src/services/TokenService.js';

const baseConfig = {
  secret: 'test-access-secret',
  refreshSecret: 'test-refresh-secret',
  expiresIn: '1h',
  refreshExpiresIn: '7d'
};

describe('[TU-AUTH-07] TokenService — emissão e verificação', () => {
  const tokens = new TokenService(baseConfig);

  test('signAccess + verifyAccess devolve o payload original', () => {
    const payload = { sub: 1, role: 'Tecnico' };
    const token = tokens.signAccess(payload);
    const decoded = tokens.verifyAccess(token);
    expect(decoded.sub).toBe(1);
    expect(decoded.role).toBe('Tecnico');
  });

  test('signRefresh + verifyRefresh devolve o payload original', () => {
    const token = tokens.signRefresh({ sub: 42 });
    const decoded = tokens.verifyRefresh(token);
    expect(decoded.sub).toBe(42);
  });

  test('access token NÃO é aceite por verifyRefresh (segredos distintos)', () => {
    const access = tokens.signAccess({ sub: 1 });
    expect(() => tokens.verifyRefresh(access)).toThrow();
  });

  test('refresh token NÃO é aceite por verifyAccess', () => {
    const refresh = tokens.signRefresh({ sub: 1 });
    expect(() => tokens.verifyAccess(refresh)).toThrow();
  });

  test('verifyAccess rejeita token com segredo diferente', () => {
    const other = new TokenService({
      ...baseConfig,
      secret: 'OUTRO-SECRET'
    });
    const tokenOther = other.signAccess({ sub: 1 });
    expect(() => tokens.verifyAccess(tokenOther)).toThrow();
  });

  test('construtor exige secret e refreshSecret', () => {
    expect(() => new TokenService({})).toThrow();
    expect(() => new TokenService({ secret: 's' })).toThrow();
  });

  test.each([null, undefined, '', 0, {}])('verifyAccess rejeita input inválido: %p', (bad) => {
    expect(() => tokens.verifyAccess(bad)).toThrow();
  });
});

describe('[TU-AUTH-08] TokenService — expiração (Análise de Valores Limite)', () => {
  test('token expirado é rejeitado', () => {
    const tokens = new TokenService({ ...baseConfig, expiresIn: '1ms' });
    const t = tokens.signAccess({ sub: 1 });
    // Espera para garantir expiração (1ms + clock tolerance 0s)
    return new Promise((resolve) => setTimeout(() => {
      expect(() => tokens.verifyAccess(t)).toThrow(/expired/i);
      resolve();
    }, 100));
  });

  test('token válido (expiração futura) é aceite', () => {
    const tokens = new TokenService({ ...baseConfig, expiresIn: '5m' });
    const t = tokens.signAccess({ sub: 1 });
    expect(() => tokens.verifyAccess(t)).not.toThrow();
  });
});
