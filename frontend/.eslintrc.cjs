module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
  ],
  ignorePatterns: ["dist", ".eslintrc.cjs", "vite.config.js"],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
  },
  settings: {
    react: { version: "18.2" },
  },
  plugins: ["react-refresh"],
  rules: {
    // React 18 automatic JSX runtime — no need to import React
    "react/jsx-uses-react": "off",
    "react/react-in-jsx-scope": "off",
    // This app uses plain JS, not TypeScript — skip prop-type validation
    "react/prop-types": "off",
    // Allow React import (harmless, some files still have it)
    "no-unused-vars": ["error", { varsIgnorePattern: "^React$" }],
    // Chinese text uses "..." punctuation — not an escaping issue
    "react/no-unescaped-entities": "off",
    // Treat refresh warnings as errors so they block CI (--max-warnings 0)
    "react-refresh/only-export-components": [
      "error",
      { allowConstantExport: true },
    ],
  },
};
