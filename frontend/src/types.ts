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
  checkin_at: string;
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

// ---- Member Reading-Interest Report ----

export interface TopicAxis {
  topic: string;
  count: number;
  pct: number;
}

export interface MemberReportAggregate {
  total_reviews: number;
  total_members: number;
  total_words: number;
  top_journals: Record<string, number>;
  topic_axes: TopicAxis[];
  member_tiers: Record<string, number>;
  cohort_summary: string;
  observations: { title: string; text: string }[];
  common_papers: CommonPaper[];
}

export interface CommonPaper {
  paper_id: number;
  review_id: number | null;
  title: string;
  journal: string;
  year: number | null;
  reader_count: number;
  readers: { user_id: number; name: string }[];
}

export interface MemberPaper {
  id: number;
  review_id?: number | null;
  title?: string;
  journal?: string;
  year?: number | null;
  comment_excerpt?: string;
  checkin_at?: string;
}

// Lightweight row in the group index member list (loaded from the index; the
// full profile is fetched lazily from the per-member endpoint).
export interface MemberSummary {
  user_id: number;
  name: string;
  review_count: number;
  word_per_review: number;
  reader_type: string;
  top_topics: string[];
}

export interface MemberProfile {
  user_id: number;
  name: string;
  review_count: number;
  total_words: number;
  word_per_review: number;
  first_checkin: string;
  last_checkin: string;
  active_months: number;
  top_journals: Record<string, number>;
  top_topics: string[];
  topic_counts: Record<string, number>;
  reader_type: string;
  portrait: string;
  reading_form: string;
  rating_scale: string;
  theme_entry: string;
  signature: string;
  papers: MemberPaper[];
}

export interface MemberReport {
  group: {
    name: string;
    display_name: string;
    desc?: string;
  };
  generated_at: string;
  generator: {
    mode: string;
    provider: string;
    model: string;
    generated_at?: string;
  };
  aggregate: MemberReportAggregate;
  members: MemberSummary[];
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

export interface CustomCheckInInterval {
  id: number;
  year: number;
  month: number;
  deadline: string;
}
