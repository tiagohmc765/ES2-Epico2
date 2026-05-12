/**
 * Testes de unidade — PasswordHasher (wrapper sobre bcrypt).
 * Mapeamento: TU-AUTH-06
 *
 * Técnica: Particionamento de Equivalência (entrada válida vs. inválida)
 * Nota: usamos rounds=4 nos testes para reduzir custo CPU sem perder validade.
 */
import { PasswordHasher } from '../../../src/services/PasswordHasher.js';

describe('[TU-AUTH-06] PasswordHasher', () => {
  const hasher = new PasswordHasher({ rounds: 4 });

  test('hash devolve string diferente da original', async () => {
    const h = await hasher.hash('Passw0rd!');
    expect(typeof h).toBe('string');
    expect(h).not.toBe('Passw0rd!');
    // bcrypt prefix
    expect(h).toMatch(/^\$2[aby]\$/);
  });

  test('hash do mesmo valor produz hashes diferentes (salt aleatório)', async () => {
    const h1 = await hasher.hash('Passw0rd!');
    const h2 = await hasher.hash('Passw0rd!');
    expect(h1).not.toBe(h2);
  });

  test('verify devolve true para password correta', async () => {
    const h = await hasher.hash('Passw0rd!');
    await expect(hasher.verify('Passw0rd!', h)).resolves.toBe(true);
  });

  test('verify devolve false para password incorreta', async () => {
    const h = await hasher.hash('Passw0rd!');
    await expect(hasher.verify('outra', h)).resolves.toBe(false);
  });

  test('hash rejeita input não-string', async () => {
    await expect(hasher.hash(null)).rejects.toThrow();
    await expect(hasher.hash(undefined)).rejects.toThrow();
    await expect(hasher.hash('')).rejects.toThrow();
  });

  test('verify devolve false (não lança) quando inputs são inválidos', async () => {
    await expect(hasher.verify(null, 'whatever')).resolves.toBe(false);
    await expect(hasher.verify('whatever', null)).resolves.toBe(false);
    await expect(hasher.verify(123, 456)).resolves.toBe(false);
  });
});
