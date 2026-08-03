import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router";
import api from "../api/client";
import ReviewCard from "../components/ReviewCard";
import Pagination from "../components/Pagination";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import { ReviewsResponse } from "../types";

interface ListProps {
  type: string;
}

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
    return <div className="alert alert-warning">请先登录</div>;
  }

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!data) return null;

  const { reviews, paginator, total_count } = data;

  return (
    <section>
      {query && (
        <div className="my-3">
          当前搜索：<span className="text-success">{query}</span>
        </div>
      )}

      {!reviews || reviews.length === 0 ? (
        <div className="my-5 text-center" style={{ minHeight: "200px" }}>
          暂无任何内容。
        </div>
      ) : (
        <>
          <div
            className="d-flex align-items-center gap-2 mb-2 text-body-secondary"
            style={{ fontSize: "0.88rem" }}
          >
            <span className="badge bg-light text-primary fw-semibold">
              {total_count} 篇
            </span>
            {paginator.num_pages > 1 && (
              <span className="text-muted">
                本页显示第 {data.start_index} - {data.end_index} 篇
              </span>
            )}
          </div>

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
