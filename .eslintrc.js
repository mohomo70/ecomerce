module.exports = {
  root: true,
  env: {
    node: true,
    es2022: true,
  },
  extends: ['eslint:recommended'],
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  rules: {
    'no-console': 'warn',
    'no-unused-vars': 'error',
  },
  ignorePatterns: [
    'node_modules/',
    'apps/web/.next/',
    'apps/web/out/',
    'apps/web/dist/',
    'apps/web/build/',
  ],
};
