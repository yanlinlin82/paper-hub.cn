import { render, screen, act, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { useApi } from "../src/hooks/useApi";

function TestComponent({ apiFunc, immediate = false }) {
  const { data, loading, error, execute } = useApi(apiFunc, immediate);
  return (
    <div>
      <div data-testid="loading">{loading ? "loading" : "idle"}</div>
      <div data-testid="data">{data ? JSON.stringify(data) : "null"}</div>
      <div data-testid="error">{error || "null"}</div>
      <button
        data-testid="execute"
        onClick={() => execute("arg1").catch(() => {})}
      >
        Execute
      </button>
    </div>
  );
}

describe("useApi", () => {
  it("starts with initial state (immediate=false)", () => {
    const apiFunc = vi.fn();
    render(<TestComponent apiFunc={apiFunc} />);
    expect(screen.getByTestId("loading").textContent).toBe("idle");
    expect(screen.getByTestId("data").textContent).toBe("null");
    expect(screen.getByTestId("error").textContent).toBe("null");
    expect(apiFunc).not.toHaveBeenCalled();
  });

  it("calls api function immediately when immediate=true", async () => {
    const apiFunc = vi.fn().mockResolvedValue("result");
    render(<TestComponent apiFunc={apiFunc} immediate={true} />);
    expect(screen.getByTestId("loading").textContent).toBe("loading");
    await waitFor(() => {
      expect(screen.getByTestId("loading").textContent).toBe("idle");
    });
    expect(screen.getByTestId("data").textContent).toBe('"result"');
    expect(apiFunc).toHaveBeenCalledTimes(1);
  });

  it("sets data on successful execution", async () => {
    const apiFunc = vi.fn().mockResolvedValue({ id: 1, name: "test" });
    render(<TestComponent apiFunc={apiFunc} />);
    await act(async () => {
      screen.getByTestId("execute").click();
    });
    await waitFor(() => {
      expect(screen.getByTestId("data").textContent).toBe(
        '{"id":1,"name":"test"}',
      );
    });
  });

  it("sets error on failed execution", async () => {
    const apiFunc = vi.fn().mockRejectedValue(new Error("Network error"));
    render(<TestComponent apiFunc={apiFunc} />);
    await act(async () => {
      screen.getByTestId("execute").click();
    });
    await waitFor(() => {
      expect(screen.getByTestId("error").textContent).toBe("Network error");
    });
  });

  it("sets generic error message when error has no message", async () => {
    const apiFunc = vi.fn().mockRejectedValue(new Error());
    render(<TestComponent apiFunc={apiFunc} />);
    await act(async () => {
      screen.getByTestId("execute").click();
    });
    await waitFor(() => {
      expect(screen.getByTestId("error").textContent).toBe("An error occurred");
    });
  });

  it("shows loading state during execution", async () => {
    let resolvePromise;
    const apiFunc = vi.fn(
      () =>
        new Promise((resolve) => {
          resolvePromise = resolve;
        }),
    );
    render(<TestComponent apiFunc={apiFunc} />);
    await act(async () => {
      screen.getByTestId("execute").click();
    });
    expect(screen.getByTestId("loading").textContent).toBe("loading");
    await act(async () => {
      resolvePromise("done");
    });
    expect(screen.getByTestId("loading").textContent).toBe("idle");
  });

  it("returns result from execute", async () => {
    const apiFunc = vi.fn().mockResolvedValue("secret");
    let returned;
    function TestWithReturn() {
      const { execute } = useApi(apiFunc);
      return (
        <button
          data-testid="exec"
          onClick={async () => {
            returned = await execute().catch(() => {});
          }}
        >
          Go
        </button>
      );
    }
    render(<TestWithReturn />);
    await act(async () => {
      await screen.getByTestId("exec").click();
    });
    expect(returned).toBe("secret");
  });
});
