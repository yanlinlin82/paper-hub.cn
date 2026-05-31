module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
    "plugin:@typescript-eslint/recommended",
  ],
  ignorePatterns: ["dist", ".eslintrc.cjs", "vite.config.ts"],
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  settings: {
    react: { version: "18.2" },
  },
  plugins: ["react-refresh"],
  rules: {
    // React 18 automatic JSX runtime — no need to import React
    "react/jsx-uses-react": "off",
    "react/react-in-jsx-scope": "off",
    // Allow React import (harmless, some files still have it)
    "react-refresh/only-export-components": [
      "error",
      { allowConstantExport: true },
    ],
    // Chinese text uses "..." punctuation — not an escaping issue
    "react/no-unescaped-entities": "off",
    // TypeScript handles prop validation
    "react/prop-types": "off",
    // Allow unused vars starting with underscore
    "@typescript-eslint/no-unused-vars": [
      "error",
      { varsIgnorePattern: "^_", argsIgnorePattern: "^_" },
    ],
  },
};
