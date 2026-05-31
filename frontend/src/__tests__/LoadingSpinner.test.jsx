import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import LoadingSpinner from "../components/LoadingSpinner";

describe("LoadingSpinner", () => {
  it("renders with default text", () => {
    render(<LoadingSpinner />);
    const texts = screen.getAllByText("加载中...");
    expect(texts.length).toBe(2);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("renders with custom text", () => {
    render(<LoadingSpinner text="正在加载数据..." />);
    const texts = screen.getAllByText("正在加载数据...");
    expect(texts.length).toBe(2);
  });

  it("renders without text when text is empty", () => {
    const { container } = render(<LoadingSpinner text="" />);
    // The visually-hidden span should still exist for accessibility
    expect(screen.getByRole("status")).toBeInTheDocument();
    // The text div should not render
    const textDivs = container.querySelectorAll(".text-body-tertiary");
    expect(textDivs.length).toBe(0);
  });
});
