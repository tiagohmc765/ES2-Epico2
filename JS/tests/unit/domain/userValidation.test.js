/**
 * Testes de unidade — Validadores do domínio User.
 *
 * Técnicas aplicadas:
 *   - Particionamento de Equivalência (PE)
 *   - Análise de Valores Limite (VL)
 *
 * Mapeamento na matriz de rastreabilidade:
 *   TU-AUTH-01 .. TU-AUTH-08
 */

import {
  isValidEmail,
  isValidPassword,
  PASSWORD_MIN_LENGTH,
  PASSWORD_MAX_LENGTH
} from '../../../src/domain/User.js';
import { isValidRole } from '../../../src/domain/User.js';
import { Roles, ALL_ROLES } from '../../../src/domain/enums.js';

describe('[TU-AUTH-01] isValidEmail — Particionamento de Equivalência', () => {
  // Classes válidas
  test.each([
    ['a@b.co'],
    ['user.name@example.com'],
    ['user+tag@example.co.uk'],
    ['MiXeDcAsE@DOMAIN.io']
  ])('aceita formato válido: %s', (email) => {
    expect(isValidEmail(email)).toBe(true);
  });

  // Classes inválidas
  test.each([
    ['', 'string vazia'],
    ['   ', 'apenas whitespace'],
    ['no-at-sign.com', 'sem @'],
    ['user@', 'sem domínio'],
    ['@domain.com', 'sem local-part'],
    ['user@domain', 'sem TLD'],
    ['user @domain.com', 'whitespace interno'],
    [null, 'null'],
    [undefined, 'undefined'],
    [123, 'tipo numérico'],
    [{}, 'objecto']
  ])('rejeita: %s (%s)', (email) => {
    expect(isValidEmail(email)).toBe(false);
  });
});

describe('[TU-AUTH-02] isValidEmail — Análise de Valores Limite (comprimento)', () => {
  // Limite superior é 254 chars no total.
  const buildEmail = (totalLen) => {
    const suffix = '@example.com'; // 12 chars
    const local = 'a'.repeat(totalLen - suffix.length);
    return local + suffix;
  };

  // Abaixo do limite — válido
  test('254 chars (limite superior) — válido', () => {
    expect(isValidEmail(buildEmail(254))).toBe(true);
  });

  // Logo acima do limite — inválido
  test('255 chars (limite superior + 1) — inválido', () => {
    expect(isValidEmail(buildEmail(255))).toBe(false);
  });

  // Valor mínimo prático: a@b.co (6 chars)
  test('email mínimo prático "a@b.co" — válido', () => {
    expect(isValidEmail('a@b.co')).toBe(true);
  });

  // Apenas 1 caractere — inválido
  test('1 char — inválido', () => {
    expect(isValidEmail('a')).toBe(false);
  });
});

describe('[TU-AUTH-03] isValidPassword — Análise de Valores Limite (comprimento)', () => {
  const passOf = (len) => {
    // construir password com 1 letra + (len-2) números + 1 letra para garantir mistura
    if (len < 2) return 'a'.repeat(len);
    return 'a' + '1'.repeat(len - 2) + 'b';
  };

  // 5 valores: abaixo, limite inferior, nominal, limite superior, acima
  test(`${PASSWORD_MIN_LENGTH - 1} chars (lim. inferior - 1) — inválido`, () => {
    expect(isValidPassword(passOf(PASSWORD_MIN_LENGTH - 1))).toBe(false);
  });
  test(`${PASSWORD_MIN_LENGTH} chars (lim. inferior) — válido`, () => {
    expect(isValidPassword(passOf(PASSWORD_MIN_LENGTH))).toBe(true);
  });
  test('valor nominal interior (32 chars) — válido', () => {
    expect(isValidPassword(passOf(32))).toBe(true);
  });
  test(`${PASSWORD_MAX_LENGTH} chars (lim. superior) — válido`, () => {
    expect(isValidPassword(passOf(PASSWORD_MAX_LENGTH))).toBe(true);
  });
  test(`${PASSWORD_MAX_LENGTH + 1} chars (lim. superior + 1) — inválido`, () => {
    expect(isValidPassword(passOf(PASSWORD_MAX_LENGTH + 1))).toBe(false);
  });
});

describe('[TU-AUTH-04] isValidPassword — Particionamento de Equivalência (composição)', () => {
  test('só letras (sem dígitos) — inválido', () => {
    expect(isValidPassword('abcdefgh')).toBe(false);
  });
  test('só dígitos (sem letras) — inválido', () => {
    expect(isValidPassword('12345678')).toBe(false);
  });
  test('letras + dígitos — válido', () => {
    expect(isValidPassword('abcd1234')).toBe(true);
  });
  test.each([null, undefined, 12345678, {}, []])('tipo inválido: %p', (val) => {
    expect(isValidPassword(val)).toBe(false);
  });
});

describe('[TU-AUTH-05] isValidRole — Particionamento de Equivalência (enum)', () => {
  // Classes válidas
  test.each(ALL_ROLES)('aceita perfil válido: %s', (role) => {
    expect(isValidRole(role)).toBe(true);
  });

  // Classes inválidas
  test.each([
    ['admin'],            // case errado
    ['ADMINISTRADOR'],    // tudo maiúsculas
    ['User'],
    [''],
    [null],
    [undefined],
    [42],
    [{}]
  ])('rejeita inválido: %p', (role) => {
    expect(isValidRole(role)).toBe(false);
  });

  test('os 3 perfis declarados são exatamente {Tecnico, Responsavel, Administrador}', () => {
    expect(new Set(ALL_ROLES)).toEqual(new Set([
      Roles.TECNICO, Roles.RESPONSAVEL, Roles.ADMINISTRADOR
    ]));
  });
});
