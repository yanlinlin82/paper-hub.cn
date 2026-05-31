import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import ScrollToTop from "../components/ScrollToTop";

describe("ScrollToTop", () => {
  beforeEach(() => {
    // Set scrollY to a value > 300 so button is visible
    Object.defineProperty(window, "scrollY", {
      value: 500,
      writable: true,
      configurable: true,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  function fireScroll() {
    act(() => {
      window.dispatchEvent(new Event("scroll"));
    });
  }

  it("renders button when scrolled past threshold", () => {
    render(<ScrollToTop />);
    fireScroll();
    expect(screen.getByLabelText("返回顶部")).toBeInTheDocument();
  });

  it("does not render button when near the top", () => {
    window.scrollY = 100;
    const { container } = render(<ScrollToTop />);
    fireScroll();
    expect(container.innerHTML).toBe("");
  });

  it("scrolls to top when clicked", () => {
    window.scrollTo = vi.fn();
    render(<ScrollToTop />);
    fireScroll();
    const button = screen.getByLabelText("返回顶部");
    button.click();
    expect(window.scrollTo).toHaveBeenCalledWith({
      top: 0,
      behavior: "smooth",
    });
  });
});
