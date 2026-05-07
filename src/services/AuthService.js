import { isValidEmail, isValidPassword, isValidRole } from '../domain/User.js';

/**
 * Erros tipados para distinguir falhas controladas de erros internos.
 */
export class AuthError extends Error {
  constructor(message, code, status = 400) {
    super(message);
    this.code = code;
    this.status = status;
    this.name = 'AuthError';
  }
}

/**
 * AuthService — orquestra registo, login e refresh.
 *
 * Dependências injetadas para facilitar substituição em testes:
 *   - userRepo: UserRepo
 *   - hasher:   PasswordHasher
 *   - tokens:   TokenService
 */
export class AuthService {
  constructor({ userRepo, hasher, tokens }) {
    if (!userRepo) throw new Error('AuthService: userRepo is required');
    if (!hasher) throw new Error('AuthService: hasher is required');
    if (!tokens) throw new Error('AuthService: tokens is required');
    this.userRepo = userRepo;
    this.hasher = hasher;
    this.tokens = tokens;
  }

  /**
   * Regista um novo utilizador.
   * Valida email, password, role e unicidade do email.
   */
  async register({ email, password, name, role }) {
    if (!isValidEmail(email)) {
      throw new AuthError('Invalid email', 'INVALID_EMAIL', 422);
    }
    if (!isValidPassword(password)) {
      throw new AuthError('Invalid password', 'INVALID_PASSWORD', 422);
    }
    if (!isValidRole(role)) {
      throw new AuthError('Invalid role', 'INVALID_ROLE', 422);
    }
    if (typeof name !== 'string' || name.trim().length === 0) {
      throw new AuthError('Invalid name', 'INVALID_NAME', 422);
    }

    const existing = this.userRepo.findByEmail(email);
    if (existing) {
      throw new AuthError('Email already in use', 'EMAIL_TAKEN', 409);
    }

    const passwordHash = await this.hasher.hash(password);
    const user = this.userRepo.create({
      email: email.trim().toLowerCase(),
      passwordHash,
      name: name.trim(),
      role,
      createdAt: new Date()
    });

    return this._publicUser(user);
  }

  /**
   * Autentica um utilizador e devolve par de tokens.
   * Decisão composta para análise MC/DC:
   *   user existe (C1) AND password verifica (C2)
   * Ambas têm de ser verdadeiras para sucesso.
   */
  async login({ email, password }) {
    if (typeof email !== 'string' || typeof password !== 'string') {
      throw new AuthError('Email and password are required', 'INVALID_CREDENTIALS', 400);
    }

    const user = this.userRepo.findByEmail(email);

    // Importante: caminho similar para utilizador inexistente vs password errada
    // (mitigar timing attacks). Em prod compararíamos contra um hash dummy.
    const ok = user
      ? await this.hasher.verify(password, user.passwordHash)
      : false;

    if (!user || !ok) {
      throw new AuthError('Invalid credentials', 'INVALID_CREDENTIALS', 401);
    }

    return this._issueTokens(user);
  }

  /**
   * Renova access token a partir de refresh token válido.
   */
  async refresh({ refreshToken }) {
    if (typeof refreshToken !== 'string' || refreshToken.length === 0) {
      throw new AuthError('Refresh token required', 'INVALID_TOKEN', 401);
    }
    let payload;
    try {
      payload = this.tokens.verifyRefresh(refreshToken);
    } catch {
      throw new AuthError('Invalid or expired refresh token', 'INVALID_TOKEN', 401);
    }
    const user = this.userRepo.findById(payload.sub);
    if (!user) {
      throw new AuthError('User not found', 'USER_NOT_FOUND', 401);
    }
    return this._issueTokens(user);
  }

  /**
   * Verifica access token e devolve utilizador associado.
   */
  authenticate(accessToken) {
    if (typeof accessToken !== 'string' || accessToken.length === 0) {
      throw new AuthError('Token required', 'INVALID_TOKEN', 401);
    }
    let payload;
    try {
      payload = this.tokens.verifyAccess(accessToken);
    } catch {
      throw new AuthError('Invalid or expired token', 'INVALID_TOKEN', 401);
    }
    const user = this.userRepo.findById(payload.sub);
    if (!user) {
      throw new AuthError('User not found', 'USER_NOT_FOUND', 401);
    }
    return this._publicUser(user);
  }

  _issueTokens(user) {
    const payload = { sub: user.id, role: user.role, email: user.email };
    return {
      user: this._publicUser(user),
      accessToken: this.tokens.signAccess(payload),
      refreshToken: this.tokens.signRefresh({ sub: user.id })
    };
  }

  _publicUser(user) {
    const { passwordHash, ...rest } = user;
    return rest;
  }
}
