import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router";
import { describe, it, expect, vi, beforeEach } from "vitest";
import type { Mock } from "vitest";

vi.mock("../src/api/client", () => ({
  default: {
    removeReview: vi.fn(),
    restoreReview: vi.fn(),
    removePaper: vi.fn(),
    editReview: vi.fn(),
    editPaper: vi.fn(),
  },
}));

import api from "../src/api/client";
import ReviewCard from "../src/components/ReviewCard";
import type { Review } from "../src/types";

const mockedApi = vi.mocked(api);

const baseReview: Review = {
  id: 7,
  creator_id: 1,
  creator_name: "Alice",
  checkin_at: "2024-01-15T10:00:00+00:00",
  comment: "Great paper",
  paper: { id: 3, title: "Test Paper", journal: "Nature" },
  is_superuser: true,
};

function renderCard(review: Review, isTrash = false) {
  return render(
    <MemoryRouter>
      <ReviewCard review={review} index={1} groupName="test" isTrash={isTrash} />
    </MemoryRouter>,
  );
}

describe("ReviewCard delete + restore", () => {
  beforeEach(() => {
    // jsdom's window.location.reload navigates and is not implemented. The
    // handlers call it on success, so force the API calls to reject so the
    // success path (and its reload) is not reached. The API call itself is
    // still recorded, which is all these tests assert.
    mockedApi.removeReview.mockReset().mockRejectedValue(new Error("boom"));
    mockedApi.restoreReview.mockReset().mockRejectedValue(new Error("boom"));
    mockedApi.removePaper.mockReset();
  });

  it("deletes only the specific review, not the whole paper", async () => {
    const user = userEvent.setup();
    renderCard(baseReview);

    await user.click(screen.getByRole("button", { name: "删除文献" }));
    await user.click(screen.getByRole("button", { name: "确认删除" }));

    await waitFor(() => {
      expect(mockedApi.removeReview).toHaveBeenCalledWith(7);
    });
    expect(mockedApi.removePaper).not.toHaveBeenCalled();
  });

  it("shows a restore button in trash and calls restoreReview", async () => {
    const user = userEvent.setup();
    renderCard(baseReview, true);

    await user.click(screen.getByRole("button", { name: "恢复" }));

    await waitFor(() => {
      expect(mockedApi.restoreReview).toHaveBeenCalledWith(7);
    });
  });

  it("shows a visible error when restoring fails", async () => {
    (mockedApi.restoreReview as Mock).mockRejectedValue(
      new Error("恢复失败"),
    );
    const user = userEvent.setup();
    renderCard(baseReview, true);

    await user.click(screen.getByRole("button", { name: "恢复" }));

    await waitFor(() => {
      expect(screen.getByText("恢复失败")).toBeInTheDocument();
    });
  });

  it("surfaces the backend error when the API returns success:false", async () => {
    (mockedApi.restoreReview as Mock).mockResolvedValue({
      success: false,
      error: "无权恢复",
    });
    const user = userEvent.setup();
    renderCard(baseReview, true);

    await user.click(screen.getByRole("button", { name: "恢复" }));

    await waitFor(() => {
      expect(screen.getByText("无权恢复")).toBeInTheDocument();
    });
  });

  it("disables the restore button and shows progress while restoring", async () => {
    let resolveRestore!: (value: unknown) => void;
    (mockedApi.restoreReview as Mock).mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveRestore = resolve;
        }),
    );
    const user = userEvent.setup();
    renderCard(baseReview, true);

    await user.click(screen.getByRole("button", { name: "恢复" }));

    await waitFor(() => {
      const pendingButton = screen.queryByRole("button", {
        name: "恢复中...",
      });
      expect(pendingButton).toBeInTheDocument();
      expect(pendingButton).toBeDisabled();
    });

    await act(async () => {
      resolveRestore({ success: true });
    });
  });
});
