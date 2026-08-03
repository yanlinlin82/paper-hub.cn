import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import { MemoryRouter } from "react-router";
import Pagination from "../src/components/Pagination";
import { Paginator } from "../src/types";

// Mock useSearchParams
const mockSetSearchParams = vi.fn();
vi.mock("react-router", async () => {
  const actual = await vi.importActual("react-router");
  return {
    ...actual,
    useSearchParams: () => [new URLSearchParams(), mockSetSearchParams],
  };
});

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("Pagination", () => {
  it("returns null when paginator is null", () => {
    const { container } = renderWithRouter(<Pagination paginator={null} />);
    expect(container.innerHTML).toBe("");
  });

  it("returns null when num_pages <= 1", () => {
    const paginator: Paginator = {
      num_pages: 1,
      number: 1,
      has_previous: false,
      has_next: false,
      previous_page_number: null,
      next_page_number: null,
    };
    const { container } = renderWithRouter(
      <Pagination paginator={paginator} />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders page numbers with current page in middle", () => {
    const paginator: Paginator = {
      number: 4,
      num_pages: 7,
      has_previous: true,
      has_next: true,
      previous_page_number: 3,
      next_page_number: 5,
    };
    renderWithRouter(<Pagination paginator={paginator} />);
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("6")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.queryByText("...")).not.toBeInTheDocument();
  });

  it("shows ellipsis for large page ranges", () => {
    const paginator: Paginator = {
      number: 1,
      num_pages: 10,
      has_previous: false,
      has_next: true,
      previous_page_number: null,
      next_page_number: 2,
    };
    renderWithRouter(<Pagination paginator={paginator} />);
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("...")).toBeInTheDocument();
  });

  it("highlights current page as active", () => {
    const paginator: Paginator = {
      number: 3,
      num_pages: 5,
      has_previous: true,
      has_next: true,
      previous_page_number: 2,
      next_page_number: 4,
    };
    renderWithRouter(<Pagination paginator={paginator} />);
    const activePage = screen.getByText("3").closest("li");
    expect(activePage).toHaveClass("active");
  });

  it("shows previous and next buttons when available", () => {
    const paginator: Paginator = {
      number: 3,
      num_pages: 5,
      has_previous: true,
      has_next: true,
      previous_page_number: 2,
      next_page_number: 4,
    };
    renderWithRouter(<Pagination paginator={paginator} />);
    expect(screen.getByText(/上一页/)).toBeInTheDocument();
    expect(screen.getByText(/下一页/)).toBeInTheDocument();
  });

  it("hides previous button on first page", () => {
    const paginator: Paginator = {
      number: 1,
      num_pages: 5,
      has_previous: false,
      has_next: true,
      previous_page_number: null,
      next_page_number: 2,
    };
    renderWithRouter(<Pagination paginator={paginator} />);
    expect(screen.queryByText(/上一页/)).not.toBeInTheDocument();
    expect(screen.getByText(/下一页/)).toBeInTheDocument();
  });

  it("hides next button on last page", () => {
    const paginator: Paginator = {
      number: 5,
      num_pages: 5,
      has_previous: true,
      has_next: false,
      previous_page_number: 4,
      next_page_number: null,
    };
    renderWithRouter(<Pagination paginator={paginator} />);
    expect(screen.getByText(/上一页/)).toBeInTheDocument();
    expect(screen.queryByText(/下一页/)).not.toBeInTheDocument();
  });

  it("calls setSearchParams when clicking a page button", async () => {
    const user = userEvent.setup();
    const paginator: Paginator = {
      number: 1,
      num_pages: 3,
      has_previous: false,
      has_next: true,
      previous_page_number: null,
      next_page_number: 2,
    };
    renderWithRouter(<Pagination paginator={paginator} />);
    await user.click(screen.getByText("2"));
    expect(mockSetSearchParams).toHaveBeenCalledWith(
      expect.any(URLSearchParams),
    );
  });
});
