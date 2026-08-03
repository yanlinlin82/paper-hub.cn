import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "react-router";
import api from "../api/client";
import ReviewCard from "../components/ReviewCard";
import Pagination from "../components/Pagination";
import LoadingSpinner from "../components/LoadingSpinner";
import { ReviewsResponse } from "../types";

function JournalReviews() {
  const { groupName, journalName } = useParams<{
    groupName: string;
    journalName: string;
  }>();
  const [searchParams] = useSearchParams();
  const [data, setData] = useState<ReviewsResponse | null>(null);
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
        const result = await api.getJournalReviews<ReviewsResponse>(
          groupName!,
          journalName!,
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
  }, [groupName, journalName, page, query]);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!data) return null;

  const journal = decodeURIComponent(journalName!);

  return (
    <section>
      <div className="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
        <div>
          <h4 className="mb-0">
            来自杂志 <i>{journal}</i> 的分享
          </h4>
          <div className="text-body-secondary small">
            浏览该杂志在社群中被分享的全部文献
          </div>
        </div>
        {data.total_count > 0 && (
          <span className="badge text-bg-primary rounded-pill">
            {data.total_count} 篇
          </span>
        )}
      </div>

      {query && (
        <div className="alert alert-secondary py-2 small mb-3">
          当前搜索：<span className="text-primary fw-semibold">{query}</span>
        </div>
      )}

      {!data.reviews || data.reviews.length === 0 ? (
        <div className="card border-0 shadow-sm">
          <div className="card-body text-center text-body-secondary py-5">
            暂无任何内容。
          </div>
        </div>
      ) : (
        <>
          {data.paginator?.num_pages > 1 && (
            <div className="text-body-secondary small mb-2">
              本页显示第 {data.start_index} - {data.end_index} 篇
            </div>
          )}
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

export default JournalReviews;
