/**
 * Middleware: extrai token Bearer e injeta utilizador autenticado em req.user.
 * Devolve 401 quando o token está em falta, é inválido ou expirou.
 */
export const authenticate = (authService) => (req, res, next) => {
  try {
    const header = req.headers['authorization'] || '';
    const [scheme, token] = header.split(' ');
    if (scheme !== 'Bearer' || !token) {
      return res.status(401).json({ error: 'Missing or malformed Authorization header' });
    }
    req.user = authService.authenticate(token);
    return next();
  } catch (err) {
    const status = err.status || 401;
    return res.status(status).json({ error: err.message, code: err.code });
  }
};
