import bcrypt from 'bcrypt';

/**
 * Wrapper sobre bcrypt para facilitar mocking em testes.
 */
export class PasswordHasher {
  constructor({ rounds = 10 } = {}) {
    this.rounds = rounds;
  }

  async hash(plainPassword) {
    if (typeof plainPassword !== 'string' || plainPassword.length === 0) {
      throw new Error('Password must be a non-empty string');
    }
    return bcrypt.hash(plainPassword, this.rounds);
  }

  async verify(plainPassword, hash) {
    if (typeof plainPassword !== 'string' || typeof hash !== 'string') {
      return false;
    }
    return bcrypt.compare(plainPassword, hash);
  }
}
