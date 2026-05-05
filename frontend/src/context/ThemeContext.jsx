import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext(null);

const STORAGE_KEY = "paperhub-theme";

function getStoredMode() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark" || stored === "system") {
      return stored;
    }
  } catch {
    /* ignore */
  }
  return "system";
}

function getSystemTheme() {
  if (typeof window === "undefined") return "dark";
  return window.matchMedia("(prefers-color-scheme: light)").matches
    ? "light"
    : "dark";
}

function applyTheme(resolved) {
  document.documentElement.setAttribute("data-bs-theme", resolved);
}

export function ThemeProvider({ children }) {
  const [mode, setModeState] = useState(getStoredMode);
  const [resolved, setResolved] = useState(() => {
    const m = getStoredMode();
    return m === "system" ? getSystemTheme() : m;
  });

  const setMode = (newMode) => {
    setModeState(newMode);
    try {
      localStorage.setItem(STORAGE_KEY, newMode);
    } catch {
      /* ignore */
    }
    const r = newMode === "system" ? getSystemTheme() : newMode;
    setResolved(r);
    applyTheme(r);
  };

  useEffect(() => {
    applyTheme(resolved);
  }, []);

  useEffect(() => {
    if (mode !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: light)");
    const handler = (e) => {
      const r = e.matches ? "light" : "dark";
      setResolved(r);
      applyTheme(r);
    };
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, [mode]);

  return (
    <ThemeContext.Provider value={{ mode, resolved, setMode }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within a ThemeProvider");
  return ctx;
}
