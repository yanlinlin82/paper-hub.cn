import { useEffect, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router";
import api from "../api/client";
import ReviewCard from "../components/ReviewCard";
import Pagination from "../components/Pagination";
import LoadingSpinner from "../components/LoadingSpinner";
import { ReviewsResponse, UserInfo } from "../types";

interface UserReviewsResponse extends ReviewsResponse {
  user_info?: UserInfo;
}

function UserReviews() {
  const { groupName, userId } = useParams<{
    groupName: string;
    userId: string;
  }>();
  const [searchParams] = useSearchParams();
  const [data, setData] = useState<UserReviewsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const page = searchParams.get("page") || "1";
  const query = searchParams.get("q") || "";

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string> = { page };
        if (query) params.q = query;
        const result = await api.getUserReviews<UserReviewsResponse>(
          groupName!,
          Number(userId),
          params,
        );
        setData(result);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [groupName, userId, page, query]);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!data) return null;

  return (
    <section>
      <div className="d-flex align-items-center gap-2 mb-2 text-body-secondary">
        来自用户{" "}
        <Link to={`/group/${groupName}/user/${data.user_info?.id || userId}`}>
          {data.user_info?.nickname || "用户"}
        </Link>{" "}
        的文献分享
      </div>

      {query && (
        <div className="my-3">
          当前搜索：<span className="text-success">{query}</span>
        </div>
      )}

      {!data.reviews || data.reviews.length === 0 ? (
        <div className="my-5 text-center" style={{ minHeight: "200px" }}>
          暂无任何内容。
        </div>
      ) : (
        <>
          <div className="d-flex align-items-center gap-2 mb-2 text-body-secondary">
            <span className="badge bg-light text-primary fw-semibold">
              {data.total_count} 篇
            </span>
            {data.paginator?.num_pages > 1 && (
              <span className="text-muted">
                本页显示第 {data.start_index} - {data.end_index} 篇
              </span>
            )}
          </div>
          <Pagination paginator={data.paginator} />
          {data.reviews.map((review, idx) => (
            <ReviewCard
              key={review.id}
              review={review}
              index={data.indices ? data.indices[idx] : data.start_index + idx}
              groupName={groupName!}
            />
          ))}
          <Pagination paginator={data.paginator} />
        </>
      )}
    </section>
  );
}

export default UserReviews;
