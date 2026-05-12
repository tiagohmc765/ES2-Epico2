import { ALL_ROLES } from './enums.js';

export class User {
  constructor({ id, email, passwordHash, name, role, createdAt = new Date() }) {
    this.id = id;
    this.email = email;
    this.passwordHash = passwordHash;
    this.name = name;
    this.role = role;
    this.createdAt = createdAt;
  }

  toPublic() {
    const { passwordHash, ...rest } = this;
    return rest;
  }
}

export const isValidRole = (role) => ALL_ROLES.includes(role);

// Regex simples para validação de email - cobre maioria dos casos comuns
export const isValidEmail = (email) => {
  if (typeof email !== 'string') return false;
  const trimmed = email.trim();
  if (trimmed.length === 0 || trimmed.length > 254) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed);
};

// Regras de password: mínimo 8 chars, máximo 128, pelo menos 1 letra e 1 número
export const PASSWORD_MIN_LENGTH = 8;
export const PASSWORD_MAX_LENGTH = 128;

export const isValidPassword = (password) => {
  if (typeof password !== 'string') return false;
  if (password.length < PASSWORD_MIN_LENGTH) return false;
  if (password.length > PASSWORD_MAX_LENGTH) return false;
  return /[A-Za-z]/.test(password) && /\d/.test(password);
};
