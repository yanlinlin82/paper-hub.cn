import React, { useEffect, useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import api from "../api/client";
import ReviewCard from "../components/ReviewCard";
import Pagination from "../components/Pagination";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";

function List({ type }) {
  const { groupName } = useParams();
  const [searchParams] = useSearchParams();
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const page = searchParams.get("page") || "1";
  const query = searchParams.get("q") || "";

  // Type labels mapping
  const typeLabels = {
    all: "所有分享",
    my_sharing: "我的分享",
    recent: "本周分享",
    this_month: "本月分享",
    last_month: "上月分享",
    trash: "回收站",
  };

  useEffect(() => {
    const fetchReviews = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = { page };
        if (query) params.q = query;
        const result = await api.getGroupReviews(groupName, {
          ...params,
          type,
        });
        setData(result);
      } catch (err) {
        setError(err.message);
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
          <div className="section-header my-3">
            <span className="count-badge">{total_count} 篇</span>
            <span>共找到 {total_count} 篇文献分享</span>
            {paginator.num_pages > 1 && (
              <span className="text-muted">
                （本页显示第 {data.start_index} - {data.end_index} 篇）
              </span>
            )}
          </div>

          <Pagination paginator={paginator} />

          {reviews.map((review, idx) => (
            <ReviewCard
              key={review.id}
              review={review}
              index={
                data.indices
                  ? data.indices[idx]
                  : (paginator.start_index || 1) + idx
              }
              groupName={groupName}
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
