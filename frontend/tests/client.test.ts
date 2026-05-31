import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import api from "../src/api/client";

interface MockResponse {
  ok: boolean;
  status: number;
  headers: {
    get: (name: string) => string | null;
  };
  json: () => Promise<unknown>;
  text: () => Promise<string>;
}

describe("API client", () => {
  const mockFetch = vi.fn();

  beforeEach(() => {
    globalThis.fetch = mockFetch;
    // Mock document.cookie for CSRF token
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "csrftoken=test-csrf-token; sessionid=abc123",
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    mockFetch.mockClear();
  });

  function mockResponse(
    data: unknown,
    status: number = 200,
    contentType: string = "application/json",
  ): MockResponse {
    return {
      ok: status >= 200 && status < 300,
      status,
      headers: {
        get: () => contentType,
      },
      json: () => Promise.resolve(data),
      text: () => Promise.resolve(JSON.stringify(data)),
    };
  }

  describe("login", () => {
    it("sends POST request with username and password", async () => {
      mockFetch.mockResolvedValue(mockResponse({ success: true }));
      const result = await api.login("testuser", "pass123");
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/login",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ username: "testuser", password: "pass123" }),
          headers: expect.objectContaining({
            "Content-Type": "application/json",
            "X-CSRFToken": "test-csrf-token",
          }),
          credentials: "same-origin",
        }),
      );
      expect(result).toEqual({ success: true });
    });
  });

  describe("logout", () => {
    it("sends POST request to /logout", async () => {
      mockFetch.mockResolvedValue(mockResponse({ success: true }));
      await api.logout();
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/logout",
        expect.objectContaining({ method: "POST" }),
      );
    });
  });

  describe("getCurrentUser", () => {
    it("sends GET request to /me/", async () => {
      mockFetch.mockResolvedValue(
        mockResponse({
          is_authenticated: true,
          username: "testuser",
        }),
      );
      const resultPromise = api.getCurrentUser();
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/me/",
        expect.objectContaining({ method: "GET" }),
      );
      await expect(resultPromise).resolves.toMatchObject({
        is_authenticated: true,
        username: "testuser",
      });
    });
  });

  describe("getGroupInfo", () => {
    it("sends GET request for group info", async () => {
      mockFetch.mockResolvedValue(
        mockResponse({ display_name: "Test Group", desc: "A test group" }),
      );
      const resultPromise = api.getGroupInfo("test-group");
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/groups/test-group/",
        expect.objectContaining({ method: "GET" }),
      );
      await expect(resultPromise).resolves.toMatchObject({
        display_name: "Test Group",
      });
    });
  });

  describe("getGroupReviews", () => {
    it("sends GET request with query parameters", async () => {
      mockFetch.mockResolvedValue(
        mockResponse({ reviews: [], total_count: 0 }),
      );
      await api.getGroupReviews("test-group", {
        page: "2",
        type: "all",
      });
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain("/api/groups/test-group/reviews/");
      expect(callUrl).toContain("page=2");
    });
  });

  describe("getGroupReview", () => {
    it("sends GET request for a single review", async () => {
      mockFetch.mockResolvedValue(
        mockResponse({ id: 42, comment: "Great paper" }),
      );
      const resultPromise = api.getGroupReview("test-group", 42);
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/groups/test-group/reviews/42/",
        expect.objectContaining({ method: "GET" }),
      );
      await expect(resultPromise).resolves.toMatchObject({
        id: 42,
      });
    });
  });

  describe("getGroupRankings", () => {
    it("sends GET request for rankings", async () => {
      mockFetch.mockResolvedValue(
        mockResponse({ ranks: [{ name: "Alice", count: 5 }] }),
      );
      await api.getGroupRankings("test-group", "this_month", {
        year: "2024",
      });
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain("/api/groups/test-group/rank/this_month/");
      expect(callUrl).toContain("year=2024");
    });
  });

  describe("getUserReviews", () => {
    it("sends GET request for user reviews", async () => {
      mockFetch.mockResolvedValue(mockResponse({ reviews: [] }));
      await api.getUserReviews("test-group", 123, { page: "1" });
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain("/api/groups/test-group/users/123/");
      expect(callUrl).toContain("page=1");
    });
  });

  describe("getJournalReviews", () => {
    it("sends GET request for journal reviews", async () => {
      mockFetch.mockResolvedValue(mockResponse({ reviews: [] }));
      await api.getJournalReviews("test-group", "Nature", {
        page: "1",
      });
      const callUrl = mockFetch.mock.calls[0][0];
      expect(callUrl).toContain("/api/groups/test-group/journals/Nature/");
      expect(callUrl).toContain("page=1");
    });
  });

  describe("checkIn", () => {
    it("sends POST request with group_name and data", async () => {
      mockFetch.mockResolvedValue(mockResponse({ success: true }));
      await api.checkIn("test-group", { paper: { title: "Test" } });
      expect(mockFetch).toHaveBeenCalledWith(
        "/api/check-in",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            group_name: "test-group",
            paper: { title: "Test" },
          }),
        }),
      );
    });
  });

  describe("error handling", () => {
    it("throws error with JSON error message on failure", async () => {
      mockFetch.mockResolvedValue(mockResponse({ error: "Not found" }, 404));
      await expect(api.getCurrentUser()).rejects.toThrow("Not found");
    });

    it("throws error with status text on non-JSON failure", async () => {
      mockFetch.mockResolvedValue(mockResponse("Not Found", 404, "text/plain"));
      await expect(api.getCurrentUser()).rejects.toThrow("Not Found");
    });

    it("throws network error for fetch failures", async () => {
      mockFetch.mockRejectedValue(new Error("Failed to fetch"));
      await expect(api.getCurrentUser()).rejects.toThrow(
        "Network error: Failed to fetch",
      );
    });
  });
});
