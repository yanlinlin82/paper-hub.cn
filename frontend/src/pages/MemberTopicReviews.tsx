import { useEffect, useState } from "react";
import { useParams, Link } from "react-router";
import api from "../api/client";
import LoadingSpinner from "../components/LoadingSpinner";
import { TopicReviewsResponse } from "../types";

function formatDate(iso: string | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

function MemberTopicReviews() {
  const { groupName, topic } = useParams<{
    groupName: string;
    topic: string;
  }>();
  const [data, setData] = useState<TopicReviewsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [year, setYear] = useState<string>("");
  const [creator, setCreator] = useState<string>("");

  useEffect(() => {
    const fetchTopic = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await api.getTopicReviews<TopicReviewsResponse>(
          groupName!,
          topic!,
        );
        setData(result);
        setYear("");
        setCreator("");
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    fetchTopic();
  }, [groupName, topic]);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!data) return null;

  const years = Array.from(
    new Set(data.reviews.map((r) => (r.year ? String(r.year) : ""))),
  )
    .sort((a, b) => (a < b ? 1 : -1))
    .filter(Boolean);
  const creators = Array.from(
    new Set(data.reviews.map((r) => r.creator_name)),
  ).sort((a, b) => a.localeCompare(b, "zh"));

  const filtered = data.reviews.filter(
    (r) =>
      (!year || String(r.year) === year) &&
      (!creator || r.creator_name === creator),
  );

  return (
    <section className="member-report">
      <header className="report-header mb-3">
        <span className="report-kicker">TOPIC REVIEWS</span>
        <h1 className="h4 mb-1">主题文献 · {data.topic}</h1>
        <p className="text-body-secondary small mb-0">
          与「{data.topic}」关联的全部文献评论。
          <Link
            className="ms-2 external-link"
            to={`/group/${groupName}/member-report`}
          >
            返回成员画像
          </Link>
        </p>
      </header>

      {data.reviews.length === 0 ? (
        <div className="card border-0 shadow-sm">
          <div className="card-body text-center text-body-secondary py-5">
            暂无该主题下的文献。
          </div>
        </div>
      ) : (
        <>
          <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
            <div className="text-body-secondary small">
              {year || creator
                ? `筛选出 ${filtered.length} / ${data.reviews.length} 篇`
                : `共 ${data.reviews.length} 篇`}
            </div>
            <div className="d-flex flex-wrap gap-2">
              <select
                className="form-select form-select-sm w-auto"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                aria-label="按年份筛选"
              >
                <option value="">全部年份</option>
                {years.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
              <select
                className="form-select form-select-sm w-auto"
                value={creator}
                onChange={(e) => setCreator(e.target.value)}
                aria-label="按分享者筛选"
              >
                <option value="">全部分享者</option>
                {creators.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="text-center text-body-secondary py-4">
              当前筛选条件下暂无文献。
            </div>
          ) : (
            filtered.map((r) => (
              <div key={r.review_id} className="report-topic-review">
                <div className="report-paper-title">
                  <Link
                    to={`/group/${groupName}/review/${r.review_id}`}
                    className="report-paper-link"
                  >
                    {r.title || "（无标题）"}
                  </Link>
                </div>
                <div className="report-topic-review-meta">
                  {r.journal && (
                    <Link
                      to={`/group/${groupName}/journal/${encodeURIComponent(r.journal)}`}
                      className="text-body-secondary"
                    >
                      {r.journal}
                    </Link>
                  )}
                  {r.year ? <span> ({r.year})</span> : null}
                  <span> · </span>
                  <Link
                    to={`/group/${groupName}/user/${r.creator_id}`}
                    className="text-body-secondary"
                  >
                    {r.creator_name}
                  </Link>
                  <span> · {formatDate(r.checkin_at)}</span>
                </div>
                {r.comment_excerpt && (
                  <div className="report-paper-comment">{r.comment_excerpt}</div>
                )}
              </div>
            ))
          )}
        </>
      )}
    </section>
  );
}

export default MemberTopicReviews;
