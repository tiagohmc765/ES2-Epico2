/**
 * Testes de unidade — AuthService.
 *
 * Técnicas aplicadas:
 *   - Particionamento de Equivalência (PE)  — register, refresh
 *   - Análise de Valores Limite (VL)        — comprimentos / id existente vs. inexistente
 *   - Cobertura de Condições Múltiplas      — login (decisão composta C1 ∧ C2)
 *
 * MC/DC sobre login (caso central da Sprint 1):
 *   Decisão: SUCESSO = (user existe) ∧ (password verifica)
 *   C1 = user existe        ; C2 = password verifica
 *   --------------------------------------
 *   |  Caso  | C1 | C2 | SUCESSO |  Teste  |
 *   |  L1    | F  | F  | F       | inexistente + password qualquer |
 *   |  L2    | F  | T  | F       | (impossível na prática — password só pode "verificar" contra um hash existente; testamos via mock: hasher.verify=true mas user=null) |
 *   |  L3    | T  | F  | F       | existente + password errada    |
 *   |  L4    | T  | T  | T       | existente + password correta   |
 *   ---------------------------------------
 *   Pares MC/DC (cada condição isoladamente afeta a decisão):
 *      C1: comparar L4 (T,T,T) vs L2 (F,T,F)  → C1 controla a decisão
 *      C2: comparar L4 (T,T,T) vs L3 (T,F,F)  → C2 controla a decisão
 *   Subconjunto mínimo MC/DC: {L2, L3, L4} (3 casos). L1 incluído para MCC completo.
 *
 * Mapeamento: TU-AUTH-09, TU-AUTH-10, TU-AUTH-11, TU-AUTH-12, TU-AUTH-13
 */

import { jest } from '@jest/globals';
import { AuthService, AuthError } from '../../../src/services/AuthService.js';
import { UserRepo } from '../../../src/repositories/memory/UserRepo.js';
import { Roles } from '../../../src/domain/enums.js';
import { fakeHasher, fakeTokens, validUserPayload } from '../../helpers/factories.js';

const buildSubject = () => {
  const userRepo = new UserRepo();
  const hasher = fakeHasher();
  const tokens = fakeTokens();
  const sut = new AuthService({ userRepo, hasher, tokens });
  return { sut, userRepo, hasher, tokens };
};

describe('[TU-AUTH-09] AuthService.register — Particionamento de Equivalência', () => {
  test('regista utilizador com payload válido (classe válida)', async () => {
    const { sut } = buildSubject();
    const u = await sut.register(validUserPayload());
    expect(u.id).toBeDefined();
    expect(u.email).toBe('tecnico@greenherb.test');
    expect(u.role).toBe(Roles.TECNICO);
    // hash não deve aparecer no objeto público
    expect(u.passwordHash).toBeUndefined();
  });

  test('email inválido → AuthError(INVALID_EMAIL, 422)', async () => {
    const { sut } = buildSubject();
    await expect(sut.register(validUserPayload({ email: 'bad' })))
      .rejects.toMatchObject({ code: 'INVALID_EMAIL', status: 422 });
  });

  test('password inválida → AuthError(INVALID_PASSWORD, 422)', async () => {
    const { sut } = buildSubject();
    await expect(sut.register(validUserPayload({ password: 'short' })))
      .rejects.toMatchObject({ code: 'INVALID_PASSWORD', status: 422 });
  });

  test('role inválido → AuthError(INVALID_ROLE, 422)', async () => {
    const { sut } = buildSubject();
    await expect(sut.register(validUserPayload({ role: 'SuperAdmin' })))
      .rejects.toMatchObject({ code: 'INVALID_ROLE', status: 422 });
  });

  test('nome em branco → AuthError(INVALID_NAME, 422)', async () => {
    const { sut } = buildSubject();
    await expect(sut.register(validUserPayload({ name: '   ' })))
      .rejects.toMatchObject({ code: 'INVALID_NAME', status: 422 });
  });

  test('email já em uso → AuthError(EMAIL_TAKEN, 409)', async () => {
    const { sut } = buildSubject();
    await sut.register(validUserPayload());
    await expect(sut.register(validUserPayload()))
      .rejects.toMatchObject({ code: 'EMAIL_TAKEN', status: 409 });
  });

  test('email é normalizado (trim + lowercase)', async () => {
    const { sut, userRepo } = buildSubject();
    await sut.register(validUserPayload({ email: '  USER@DOMAIN.COM  ' }));
    expect(userRepo.findByEmail('user@domain.com')).not.toBeNull();
  });
});

describe('[TU-AUTH-10] AuthService.login — Cobertura de Condições Múltiplas (MC/DC)', () => {
  // Setup partilhado: cria um utilizador conhecido
  const setup = async () => {
    const tools = buildSubject();
    await tools.sut.register(validUserPayload());
    return tools;
  };

  test('L1: user inexistente + password qualquer (C1=F,C2=F) → 401', async () => {
    const { sut } = await setup();
    await expect(sut.login({ email: 'no@one.com', password: 'wrong' }))
      .rejects.toMatchObject({ code: 'INVALID_CREDENTIALS', status: 401 });
  });

  test('L2: user inexistente + hasher devolveria true (C1=F,C2=T) → 401', async () => {
    // Forçamos hasher.verify => true para isolar C1
    const { sut, userRepo, tokens } = buildSubject();
    const hasherAlwaysTrue = { hash: async (p) => `hashed:${p}`, verify: async () => true };
    const sut2 = new AuthService({ userRepo, hasher: hasherAlwaysTrue, tokens });
    await expect(sut2.login({ email: 'ghost@x.com', password: 'whatever' }))
      .rejects.toMatchObject({ code: 'INVALID_CREDENTIALS', status: 401 });
  });

  test('L3: user existe + password errada (C1=T,C2=F) → 401', async () => {
    const { sut } = await setup();
    await expect(sut.login({ email: 'tecnico@greenherb.test', password: 'errada' }))
      .rejects.toMatchObject({ code: 'INVALID_CREDENTIALS', status: 401 });
  });

  test('L4: user existe + password correta (C1=T,C2=T) → tokens', async () => {
    const { sut } = await setup();
    const r = await sut.login({ email: 'tecnico@greenherb.test', password: 'Passw0rd!' });
    expect(r.accessToken).toBeDefined();
    expect(r.refreshToken).toBeDefined();
    expect(r.user.passwordHash).toBeUndefined();
    expect(r.user.role).toBe(Roles.TECNICO);
  });

  test('Resposta de erro NÃO distingue user inexistente de password errada', async () => {
    const { sut } = await setup();
    let e1, e2;
    try { await sut.login({ email: 'no@one.com', password: 'x' }); }
    catch (e) { e1 = e; }
    try { await sut.login({ email: 'tecnico@greenherb.test', password: 'errada' }); }
    catch (e) { e2 = e; }
    // Mensagem e código devem ser iguais — defesa contra enumeração
    expect(e1.code).toBe(e2.code);
    expect(e1.message).toBe(e2.message);
    expect(e1.status).toBe(e2.status);
  });

  test('email é normalizado no login (case-insensitive)', async () => {
    const { sut } = await setup();
    const r = await sut.login({ email: 'TECNICO@GREENHERB.TEST', password: 'Passw0rd!' });
    expect(r.accessToken).toBeDefined();
  });

  test('inputs com tipos errados → AuthError(INVALID_CREDENTIALS, 400)', async () => {
    const { sut } = await setup();
    await expect(sut.login({ email: null, password: 'x' }))
      .rejects.toMatchObject({ status: 400 });
    await expect(sut.login({ email: 'x@y.com', password: 12345 }))
      .rejects.toMatchObject({ status: 400 });
  });
});

describe('[TU-AUTH-11] AuthService.refresh — Particionamento de Equivalência', () => {
  test('refresh válido devolve novo par de tokens', async () => {
    const { sut } = buildSubject();
    await sut.register(validUserPayload());
    const login = await sut.login({ email: 'tecnico@greenherb.test', password: 'Passw0rd!' });
    const r = await sut.refresh({ refreshToken: login.refreshToken });
    expect(r.accessToken).toBeDefined();
    expect(r.refreshToken).toBeDefined();
  });

  test.each([null, undefined, '', 0, {}])('refresh inválido %p → AuthError(INVALID_TOKEN, 401)', async (bad) => {
    const { sut } = buildSubject();
    await expect(sut.refresh({ refreshToken: bad }))
      .rejects.toMatchObject({ code: 'INVALID_TOKEN', status: 401 });
  });

  test('refresh com token corrompido → AuthError(INVALID_TOKEN, 401)', async () => {
    const { sut } = buildSubject();
    await expect(sut.refresh({ refreshToken: 'definitivamente-nao-e-um-token' }))
      .rejects.toMatchObject({ code: 'INVALID_TOKEN', status: 401 });
  });

  test('refresh com token válido mas user removido → USER_NOT_FOUND, 401', async () => {
    const { sut, userRepo } = buildSubject();
    await sut.register(validUserPayload());
    const login = await sut.login({ email: 'tecnico@greenherb.test', password: 'Passw0rd!' });
    // Apaga o user
    userRepo.clear();
    await expect(sut.refresh({ refreshToken: login.refreshToken }))
      .rejects.toMatchObject({ code: 'USER_NOT_FOUND', status: 401 });
  });
});

describe('[TU-AUTH-12] AuthService.authenticate — token check', () => {
  test('access token válido devolve utilizador', async () => {
    const { sut } = buildSubject();
    await sut.register(validUserPayload());
    const login = await sut.login({ email: 'tecnico@greenherb.test', password: 'Passw0rd!' });
    const u = sut.authenticate(login.accessToken);
    expect(u.email).toBe('tecnico@greenherb.test');
    expect(u.passwordHash).toBeUndefined();
  });

  test.each([null, undefined, '', 0])('token inválido %p → INVALID_TOKEN, 401', (bad) => {
    const { sut } = buildSubject();
    expect(() => sut.authenticate(bad)).toThrow(AuthError);
    try { sut.authenticate(bad); } catch (e) { expect(e.status).toBe(401); }
  });

  test('access token com refresh secret é rejeitado', async () => {
    const { sut, tokens } = buildSubject();
    await sut.register(validUserPayload());
    const refresh = tokens.signRefresh({ sub: 1 });
    expect(() => sut.authenticate(refresh)).toThrow();
  });
});

describe('[TU-AUTH-13] AuthService — construtor exige dependências', () => {
  test('faltando userRepo lança erro', () => {
    expect(() => new AuthService({ hasher: {}, tokens: {} })).toThrow(/userRepo/);
  });
  test('faltando hasher lança erro', () => {
    expect(() => new AuthService({ userRepo: {}, tokens: {} })).toThrow(/hasher/);
  });
  test('faltando tokens lança erro', () => {
    expect(() => new AuthService({ userRepo: {}, hasher: {} })).toThrow(/tokens/);
  });
});
