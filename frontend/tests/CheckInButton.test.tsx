import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";

vi.mock("../src/api/client", () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

import api from "../src/api/client";
import CheckInButton from "../src/components/CheckInButton";

const mockedApi = vi.mocked(api);

describe("CheckInButton submit guard", () => {
  beforeEach(() => {
    mockedApi.get.mockReset();
    mockedApi.post.mockReset();
    mockedApi.get.mockResolvedValue({ users: [] });
  });

  it("disables the submit button and shows progress while the request is pending", async () => {
    // A promise we control, so the request stays in-flight until we resolve it.
    let resolvePost!: (value: unknown) => void;
    mockedApi.post.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePost = resolve;
        }),
    );

    const user = userEvent.setup();
    render(<CheckInButton groupName="test-group" />);

    await user.click(screen.getByRole("button", { name: "+ 分享打卡" }));
    await user.type(screen.getByPlaceholderText("用户名"), "Alice");

    await user.click(screen.getByRole("button", { name: "提交" }));

    // While the request is in-flight the submit button must be disabled.
    await waitFor(() => {
      const pendingButton = screen.queryByRole("button", {
        name: "提交中...",
      });
      expect(pendingButton).toBeInTheDocument();
      expect(pendingButton).toBeDisabled();
    });

    expect(mockedApi.post).toHaveBeenCalledTimes(1);
    expect(mockedApi.post).toHaveBeenCalledWith(
      "/check-in",
      expect.objectContaining({
        group_name: "test-group",
        admin_user: "Alice",
      }),
    );

    // Resolve the request to avoid leaking a dangling promise.
    await act(async () => {
      resolvePost({ success: false });
    });
  });
});
