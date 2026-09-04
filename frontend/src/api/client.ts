/**
 * API client for communicating with the Django backend.
 */
import type { RequestOptions } from "../types";

const API_BASE = "/api";

interface ApiErrorData {
  error?: string;
  [key: string]: unknown;
}

class ApiError extends Error {
  status: number;
  data: ApiErrorData | string;

  constructor(message: string, status: number, data: ApiErrorData | string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

function getCookie(name: string): string | null {
  let cookieValue: string | null = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function request<T = unknown>(
  method: string,
  url: string,
  data: Record<string, unknown> | null = null,
  options: RequestOptions = {},
): Promise<T> {
  const config: RequestInit & { headers: Record<string, string> } = {
    method,
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken") ?? "",
      ...options.headers,
    },
    credentials: "same-origin",
    // Never cache API responses — the member-report data is regenerated
    // server-side, and stale browser/HTTP caches would show old results.
    cache: "no-store",
    ...options,
  };

  if (data && method !== "GET") {
    config.body = JSON.stringify(data);
  }

  const fullUrl = `${API_BASE}${url}`;

  try {
    const response = await fetch(fullUrl, config);
    const contentType = response.headers.get("content-type");
    let result: T | string;

    if (contentType && contentType.includes("application/json")) {
      result = (await response.json()) as T;
    } else {
      result = await response.text();
    }

    if (!response.ok) {
      const errorData = result as ApiErrorData | string;
      const message =
        typeof errorData === "object" && errorData.error
          ? errorData.error
          : typeof errorData === "string"
            ? errorData
            : `HTTP ${response.status}`;
      throw new ApiError(message, response.status, errorData);
    }

    return result as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new Error("Network error: " + (error as Error).message);
  }
}

const api = {
  get: <T = unknown>(url: string, options?: RequestOptions) =>
    request<T>("GET", url, null, options),
  post: <T = unknown>(
    url: string,
    data?: Record<string, unknown>,
    options?: RequestOptions,
  ) => request<T>("POST", url, data ?? null, options),
  put: <T = unknown>(
    url: string,
    data?: Record<string, unknown>,
    options?: RequestOptions,
  ) => request<T>("PUT", url, data ?? null, options),
  patch: <T = unknown>(
    url: string,
    data?: Record<string, unknown>,
    options?: RequestOptions,
  ) => request<T>("PATCH", url, data ?? null, options),
  delete: <T = unknown>(url: string, options?: RequestOptions) =>
    request<T>("DELETE", url, null, options),

  // Auth
  login: (username: string, password: string) =>
    request("POST", "/login", { username, password }),
  logout: () => request("POST", "/logout"),

  // Group reviews
  getGroupInfo: <T = unknown>(groupName: string) =>
    request<T>("GET", `/groups/${groupName}/`),
  getGroupReviews: <T = unknown>(
    groupName: string,
    params: Record<string, string> = {},
  ) => {
    const query = new URLSearchParams(params).toString();
    return request<T>(
      "GET",
      `/groups/${groupName}/reviews/${query ? "?" + query : ""}`,
    );
  },
  getGroupReview: <T = unknown>(groupName: string, reviewId: number) =>
    request<T>("GET", `/groups/${groupName}/reviews/${reviewId}/`),
  getGroupRankings: <T = unknown>(
    groupName: string,
    rankType: string,
    params: Record<string, string> = {},
  ) => {
    const query = new URLSearchParams(params).toString();
    const url = `/groups/${groupName}/rank/${rankType}/${query ? "?" + query : ""}`;
    return request<T>("GET", url);
  },
  getUserReviews: <T = unknown>(
    groupName: string,
    userId: number,
    params: Record<string, string> = {},
  ) => {
    const query = new URLSearchParams(params).toString();
    return request<T>(
      "GET",
      `/groups/${groupName}/users/${userId}/${query ? "?" + query : ""}`,
    );
  },
  getJournalReviews: <T = unknown>(
    groupName: string,
    journalName: string,
    params: Record<string, string> = {},
  ) => {
    const query = new URLSearchParams(params).toString();
    return request<T>(
      "GET",
      `/groups/${groupName}/journals/${encodeURIComponent(journalName)}/${query ? "?" + query : ""}`,
    );
  },
  getMemberReport: <T = unknown>(groupName: string) =>
    request<T>("GET", `/groups/${groupName}/member-report/`),
  getMemberProfile: <T = unknown>(groupName: string, userId: number) =>
    request<T>("GET", `/groups/${groupName}/member-report/${userId}/`),

  // User
  getCurrentUser: <T = unknown>() => request<T>("GET", "/me/"),
  checkIn: <T = unknown>(groupName: string, data: Record<string, unknown>) =>
    request<T>("POST", "/check-in", { group_name: groupName, ...data }),

  // Edit & delete
  editReview: <T = unknown>(
    reviewId: number,
    comment: string,
    checkinAt: string,
  ) =>
    request<T>("POST", "/new-edit-review", {
      review_id: reviewId,
      comment,
      checkin_at: checkinAt,
    }),
  removeReview: <T = unknown>(reviewId: number) =>
    request<T>("POST", "/new-remove-review", { review_id: reviewId }),
  restoreReview: <T = unknown>(reviewId: number) =>
    request<T>("POST", "/new-restore-review", { review_id: reviewId }),
  editPaper: <T = unknown>(
    reviewId: number,
    paperId: number,
    paperData: Record<string, unknown>,
  ) =>
    request<T>("POST", "/submit-review", {
      review_id: reviewId,
      paper_id: paperId,
      ...paperData,
    }),
  removePaper: <T = unknown>(paperId: number) =>
    request<T>("POST", "/new-remove-paper", { paper_id: paperId }),

  // Translation
  translateTitle: <T = unknown>(paperId: number, title: string) =>
    request<T>("POST", "/translate-title", { paper_id: paperId, title }),
  translateAbstract: <T = unknown>(paperId: number, abstract: string) =>
    request<T>("POST", "/translate-abstract", {
      paper_id: paperId,
      abstract,
    }),

  // Custom check-in intervals
  listCustomCheckinIntervals: <T = unknown>() =>
    request<T>("GET", "/custom-checkin-intervals/"),
  createCustomCheckinInterval: <T = unknown>(data: Record<string, unknown>) =>
    request<T>("POST", "/custom-checkin-intervals/create/", data),
  updateCustomCheckinInterval: <T = unknown>(
    intervalId: number,
    data: Record<string, unknown>,
  ) => request<T>("POST", `/custom-checkin-intervals/${intervalId}/`, data),
  deleteCustomCheckinInterval: <T = unknown>(intervalId: number) =>
    request<T>("POST", `/custom-checkin-intervals/${intervalId}/delete/`),
};

export default api;
