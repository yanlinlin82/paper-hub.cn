import { useEffect, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router";
import api from "../api/client";
import ReviewCard from "../components/ReviewCard";
import Pagination from "../components/Pagination";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import { ReviewsResponse } from "../types";

interface ListProps {
  type: string;
}

const TITLES: Record<string, string> = {
  all: "所有分享",
  my_sharing: "我的分享",
  recent: "近期分享",
  this_month: "本月分享",
  last_month: "上月分享",
  trash: "回收站",
};

function List({ type }: ListProps) {
  const { groupName } = useParams<{ groupName: string }>();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();
  const [data, setData] = useState<ReviewsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const page = searchParams.get("page") || "1";
  const query = searchParams.get("q") || "";

  useEffect(() => {
    const fetchReviews = async () => {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string> = { page };
        if (query) params.q = query;
        const result = await api.getGroupReviews<ReviewsResponse>(groupName!, {
          ...params,
          type,
        });
        setData(result);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    fetchReviews();
  }, [groupName, type, page, query]);

  // Check access for my_sharing and trash
  if ((type === "my_sharing" || type === "trash") && !user) {
    return (
      <div className="alert alert-warning">
        请先登录后再查看该页面。
      </div>
    );
  }

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!data) return null;

  const { reviews, paginator, total_count } = data;

  return (
    <section>
      <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
        <h4 className="mb-0">{TITLES[type] || "文献分享"}</h4>
        {total_count > 0 && (
          <span className="badge text-bg-primary rounded-pill">
            {total_count} 篇
          </span>
        )}
      </div>

      {query && (
        <div className="alert alert-secondary py-2 small mb-3">
          当前搜索：<span className="text-primary fw-semibold">{query}</span>
          <Link to={`/group/${groupName}/${type}`} className="ms-2 external-link">
            清除搜索
          </Link>
        </div>
      )}

      {!reviews || reviews.length === 0 ? (
        <div className="card border-0 shadow-sm">
          <div className="card-body text-center text-body-secondary py-5">
            暂无任何内容。
          </div>
        </div>
      ) : (
        <>
          {paginator.num_pages > 1 && (
            <div className="text-body-secondary small mb-2">
              本页显示第 {data.start_index} - {data.end_index} 篇
            </div>
          )}

          <Pagination paginator={paginator} />

          {reviews.map((review, idx) => (
            <ReviewCard
              key={review.id}
              review={review}
              index={data.indices ? data.indices[idx] : data.start_index + idx}
              groupName={groupName!}
              isTrash={type === "trash"}
            />
          ))}

          <Pagination paginator={paginator} />
        </>
      )}
    </section>
  );
}

export default List;
