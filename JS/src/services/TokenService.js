import jwt from 'jsonwebtoken';

/**
 * Wrapper sobre jsonwebtoken para emitir e validar tokens.
 * Separa access token (curto) de refresh token (longo) com segredos distintos.
 */
export class TokenService {
  constructor({ secret, expiresIn = '15m', refreshSecret, refreshExpiresIn = '7d' }) {
    if (!secret) throw new Error('TokenService: secret is required');
    if (!refreshSecret) throw new Error('TokenService: refreshSecret is required');
    this.secret = secret;
    this.expiresIn = expiresIn;
    this.refreshSecret = refreshSecret;
    this.refreshExpiresIn = refreshExpiresIn;
  }

  signAccess(payload) {
    return jwt.sign(payload, this.secret, { expiresIn: this.expiresIn });
  }

  signRefresh(payload) {
    return jwt.sign(payload, this.refreshSecret, { expiresIn: this.refreshExpiresIn });
  }

  verifyAccess(token) {
    if (typeof token !== 'string' || token.length === 0) {
      throw new Error('Invalid token');
    }
    return jwt.verify(token, this.secret);
  }

  verifyRefresh(token) {
    if (typeof token !== 'string' || token.length === 0) {
      throw new Error('Invalid token');
    }
    return jwt.verify(token, this.refreshSecret);
  }

  decode(token) {
    return jwt.decode(token);
  }
}
