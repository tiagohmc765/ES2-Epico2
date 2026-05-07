import { AuthError } from '../services/AuthService.js';

/**
 * Handler global de erros — converte erros conhecidos em respostas JSON
 * e mantém compatibilidade com formatos esperados pelos testes.
 */
// eslint-disable-next-line no-unused-vars
export const errorHandler = (err, req, res, next) => {
  if (err instanceof AuthError) {
    return res.status(err.status).json({ error: err.message, code: err.code });
  }
  if (err && err.status && err.message) {
    return res.status(err.status).json({ error: err.message });
  }
  console.error('Unhandled error:', err);
  return res.status(500).json({ error: 'Internal server error' });
};
