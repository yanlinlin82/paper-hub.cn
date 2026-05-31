// ---- API Response Types ----

export interface Paper {
  id: number;
  title?: string;
  journal?: string;
  journal_impact_factor?: string;
  journal_impact_factor_quartile?: number;
  pub_date?: string;
  authors?: string;
  abstract?: string;
  keywords?: string;
  urls?: string;
  doi?: string;
  pmid?: string;
  pmcid?: string;
  arxiv_id?: string;
  cnki_id?: string;
}

export interface Review {
  id: number;
  creator_id: number;
  creator_name: string;
  checkin_at: string;
  comment: string;
  paper?: Paper;
  is_superuser?: boolean;
}

export interface Paginator {
  number: number;
  num_pages: number;
  has_previous: boolean;
  has_next: boolean;
  previous_page_number: number | null;
  next_page_number: number | null;
}

export interface ReviewsResponse {
  reviews: Review[];
  paginator: Paginator;
  total_count: number;
  start_index: number;
  end_index: number;
  indices?: number[];
}

export interface User {
  is_authenticated: boolean;
  username: string;
  is_superuser?: boolean;
  nickname?: string;
  id?: number;
}

export interface LoginResponse {
  success: boolean;
  error?: string;
}

export interface GroupInfo {
  display_name: string;
  desc?: string;
}

export interface RankEntry {
  display_index: number;
  name: string;
  count: number;
  create_time: string;
  id?: number;
}

export interface RankingsResponse {
  ranks: RankEntry[];
  year?: string;
  month?: string;
  year_list?: string[];
  month_list?: string[];
}

export interface UserInfo {
  id: number;
  nickname?: string;
}

// ---- Auth Context Types ----

export interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<LoginResponse>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
}

// ---- Theme Context Types ----

export type ThemeMode = "light" | "dark" | "system";

export interface ThemeContextValue {
  mode: ThemeMode;
  resolved: "light" | "dark";
  setMode: (mode: ThemeMode) => void;
}

// ---- Request Options ----

export interface RequestOptions {
  headers?: Record<string, string>;
  [key: string]: unknown;
}
