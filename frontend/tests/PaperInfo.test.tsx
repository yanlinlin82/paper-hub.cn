import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { MemoryRouter } from "react-router-dom";
import PaperInfo from "../src/components/PaperInfo";
import type { Paper } from "../src/types";

function renderWithRouter(ui: React.ReactElement) {
  return render(<MemoryRouter>{ui}</MemoryRouter>);
}

describe("PaperInfo", () => {
  it("renders nothing when paper is null", () => {
    const { container } = renderWithRouter(
      <PaperInfo paper={null} groupName="test" />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders nothing when paper is undefined", () => {
    const { container } = renderWithRouter(
      <PaperInfo paper={undefined} groupName="test" />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders journal with impact factor and quartile", () => {
    const paper: Paper = {
      id: 1,
      journal_impact_factor: "5.2",
      journal_impact_factor_quartile: 1,
      journal: "Nature",
      pub_date: "2024-01-15",
    };
    renderWithRouter(<PaperInfo paper={paper} groupName="test" />);
    expect(screen.getByText(/IF:5\.2/)).toBeInTheDocument();
    expect(screen.getByText("Q1")).toBeInTheDocument();
    expect(screen.getByText(/Nature/)).toBeInTheDocument();
  });

  it("renders journal link", () => {
    const paper: Paper = {
      id: 2,
      journal: "Nature",
      pub_date: "2024-01-15",
    };
    renderWithRouter(<PaperInfo paper={paper} groupName="test" />);
    const journalLink = screen.getByText(/Nature/);
    expect(journalLink.closest("a") as HTMLElement).toHaveAttribute(
      "href",
      "/group/test/journal/Nature",
    );
  });

  it("renders DOI link", () => {
    const paper: Paper = {
      id: 3,
      doi: "10.1234/example",
      pub_date: "2024-01-15",
    };
    renderWithRouter(<PaperInfo paper={paper} groupName="test" />);
    expect(screen.getByText("10.1234/example")).toBeInTheDocument();
    expect(
      screen.getByText("10.1234/example").closest("a") as HTMLElement,
    ).toHaveAttribute("href", "https://doi.org/10.1234/example");
  });

  it("renders PMID link", () => {
    const paper: Paper = {
      id: 4,
      pmid: "12345678",
      pub_date: "2024-01-15",
    };
    renderWithRouter(<PaperInfo paper={paper} groupName="test" />);
    expect(
      screen.getByText("12345678").closest("a") as HTMLElement,
    ).toHaveAttribute("href", "https://pubmed.ncbi.nlm.nih.gov/12345678");
  });

  it("renders PMCID link", () => {
    const paper: Paper = {
      id: 5,
      pmcid: "PMC1234567",
      pub_date: "2024-01-15",
    };
    renderWithRouter(<PaperInfo paper={paper} groupName="test" />);
    expect(
      screen.getByText("PMC1234567").closest("a") as HTMLElement,
    ).toHaveAttribute(
      "href",
      "http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567",
    );
  });

  it("renders arXiv link", () => {
    const paper: Paper = {
      id: 6,
      arxiv_id: "2401.00001",
      pub_date: "2024-01-15",
    };
    renderWithRouter(<PaperInfo paper={paper} groupName="test" />);
    expect(
      screen.getByText("2401.00001").closest("a") as HTMLElement,
    ).toHaveAttribute("href", "https://arxiv.org/abs/2401.00001");
  });

  it("renders all identifiers together", () => {
    const paper: Paper = {
      id: 7,
      doi: "10.1234/test",
      pmid: "99999999",
      pmcid: "PMC999999",
      arxiv_id: "2401.99999",
      cnki_id: "CJFD2024TEST",
      journal: "Science",
      pub_date: "2024-06-01",
    };
    renderWithRouter(<PaperInfo paper={paper} groupName="test" />);
    expect(screen.getByText("10.1234/test")).toBeInTheDocument();
    expect(screen.getByText("99999999")).toBeInTheDocument();
    expect(screen.getByText("PMC999999")).toBeInTheDocument();
    expect(screen.getByText("2401.99999")).toBeInTheDocument();
    expect(screen.getByText("CJFD2024TEST")).toBeInTheDocument();
  });
});
