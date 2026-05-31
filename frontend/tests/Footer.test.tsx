import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import Footer from "../src/components/Footer";

describe("Footer", () => {
  it("renders copyright link", () => {
    render(<Footer />);
    const link = screen.getByText(/© 2022 - 2024/i);
    expect(link).toBeInTheDocument();
    expect((link.closest("a") as HTMLElement)).toHaveAttribute(
      "href",
      "https://yanlinlin.cn/",
    );
  });

  it("renders ICP备案号 link", () => {
    render(<Footer />);
    const link = screen.getByText(/京ICP备18031542号-9/i);
    expect(link).toBeInTheDocument();
    expect((link.closest("a") as HTMLElement)).toHaveAttribute(
      "href",
      "http://beian.miit.gov.cn/",
    );
  });

  it("renders GitHub link", () => {
    render(<Footer />);
    const link = screen.getByText(/GitHub/i);
    expect(link).toBeInTheDocument();
    expect((link.closest("a") as HTMLElement)).toHaveAttribute(
      "href",
      "https://github.com/yanlinlin82/paper-hub.cn/",
    );
  });

  it("renders technology stack credits", () => {
    render(<Footer />);
    expect(screen.getByText(/Django/)).toBeInTheDocument();
    expect(screen.getByText(/Bootstrap/)).toBeInTheDocument();
    expect(screen.getByText(/React/)).toBeInTheDocument();
  });
});
