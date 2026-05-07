import 'dotenv/config';

const required = (name, fallback) => {
  const value = process.env[name];
  if (value !== undefined && value !== '') return value;
  if (fallback !== undefined) return fallback;
  throw new Error(`Missing required environment variable: ${name}`);
};

export const config = {
  port: parseInt(required('PORT', '3000'), 10),
  env: required('NODE_ENV', 'development'),
  jwt: {
    secret: required('JWT_SECRET', 'dev_secret_change_me'),
    expiresIn: required('JWT_EXPIRES_IN', '15m'),
    refreshSecret: required('JWT_REFRESH_SECRET', 'dev_refresh_secret_change_me'),
    refreshExpiresIn: required('JWT_REFRESH_EXPIRES_IN', '7d')
  },
  bcrypt: {
    rounds: parseInt(required('BCRYPT_ROUNDS', '10'), 10)
  }
};

export default config;
