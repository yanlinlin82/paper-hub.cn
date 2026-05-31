import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { ThemeProvider, useTheme } from "../src/context/ThemeContext";

// Helper component to test the hook
function TestConsumer() {
  const { mode, resolved, setMode } = useTheme();
  return (
    <div>
      <span data-testid="mode">{mode}</span>
      <span data-testid="resolved">{resolved}</span>
      <button data-testid="set-light" onClick={() => setMode("light")}>
        Light
      </button>
      <button data-testid="set-dark" onClick={() => setMode("dark")}>
        Dark
      </button>
      <button data-testid="set-system" onClick={() => setMode("system")}>
        System
      </button>
    </div>
  );
}

describe("ThemeContext", () => {
  beforeEach(() => {
    localStorage.clear();
    // Set system preference to dark by default
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: query === "(prefers-color-scheme: light)" ? false : true,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      })),
    });
  });

  it("defaults to system mode", () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId("mode").textContent).toBe("system");
    expect(screen.getByTestId("resolved").textContent).toBe("dark");
  });

  it("uses stored mode from localStorage", () => {
    localStorage.setItem("paperhub-theme", "light");
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    expect(screen.getByTestId("mode").textContent).toBe("light");
    expect(screen.getByTestId("resolved").textContent).toBe("light");
  });

  it("switches to light mode", () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    act(() => {
      screen.getByTestId("set-light").click();
    });
    expect(screen.getByTestId("mode").textContent).toBe("light");
    expect(screen.getByTestId("resolved").textContent).toBe("light");
    expect(localStorage.getItem("paperhub-theme")).toBe("light");
  });

  it("switches to dark mode", () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    act(() => {
      screen.getByTestId("set-dark").click();
    });
    expect(screen.getByTestId("mode").textContent).toBe("dark");
    expect(screen.getByTestId("resolved").textContent).toBe("dark");
    expect(localStorage.getItem("paperhub-theme")).toBe("dark");
  });

  it("switches back to system mode", () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    act(() => {
      screen.getByTestId("set-light").click();
    });
    act(() => {
      screen.getByTestId("set-system").click();
    });
    expect(screen.getByTestId("mode").textContent).toBe("system");
  });

  it("updates data-bs-theme attribute on document", () => {
    render(
      <ThemeProvider>
        <TestConsumer />
      </ThemeProvider>,
    );
    act(() => {
      screen.getByTestId("set-light").click();
    });
    expect(
      document.documentElement.getAttribute("data-bs-theme"),
    ).toBe("light");

    act(() => {
      screen.getByTestId("set-dark").click();
    });
    expect(
      document.documentElement.getAttribute("data-bs-theme"),
    ).toBe("dark");
  });

  it("throws when useTheme is used outside provider", () => {
    // Suppress console.error for this expected error
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<TestConsumer />)).toThrow(
      "useTheme must be used within a ThemeProvider",
    );
    consoleSpy.mockRestore();
  });
});
