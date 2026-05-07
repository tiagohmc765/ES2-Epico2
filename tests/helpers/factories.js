import { Roles } from '../../src/domain/enums.js';

export const validUserPayload = (overrides = {}) => ({
  email: 'tecnico@greenherb.test',
  password: 'Passw0rd!',
  name: 'Tecnico Teste',
  role: Roles.TECNICO,
  ...overrides
});

/**
 * Mock simples de PasswordHasher (sem bcrypt para testes rápidos e determinísticos).
 */
export const fakeHasher = () => ({
  async hash(p) { return `hashed:${p}`; },
  async verify(p, h) { return h === `hashed:${p}`; }
});

/**
 * Mock simples de TokenService.
 */
export const fakeTokens = () => {
  const issued = new Map();
  return {
    signAccess: (payload) => {
      const t = `access.${JSON.stringify(payload)}`;
      issued.set(t, payload);
      return t;
    },
    signRefresh: (payload) => {
      const t = `refresh.${JSON.stringify(payload)}`;
      issued.set(t, payload);
      return t;
    },
    verifyAccess: (t) => {
      if (!issued.has(t) || !t.startsWith('access.')) throw new Error('bad');
      return issued.get(t);
    },
    verifyRefresh: (t) => {
      if (!issued.has(t) || !t.startsWith('refresh.')) throw new Error('bad');
      return issued.get(t);
    }
  };
};
