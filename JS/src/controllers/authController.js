/**
 * Controllers para /auth.
 * Cada handler é gerado a partir do AuthService injetado.
 */
export const buildAuthController = (authService) => ({
  async register(req, res, next) {
    try {
      const user = await authService.register(req.body || {});
      res.status(201).json(user);
    } catch (err) { next(err); }
  },

  async login(req, res, next) {
    try {
      const result = await authService.login(req.body || {});
      res.status(200).json(result);
    } catch (err) { next(err); }
  },

  async refresh(req, res, next) {
    try {
      const result = await authService.refresh(req.body || {});
      res.status(200).json(result);
    } catch (err) { next(err); }
  },

  async me(req, res) {
    res.status(200).json(req.user);
  }
});
