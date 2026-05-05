import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import api from '../api/client';
import ReviewCard from '../components/ReviewCard';
import Pagination from '../components/Pagination';
import LoadingSpinner from '../components/LoadingSpinner';

function UserReviews() {
  const { groupName, userId } = useParams();
  const [searchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const page = searchParams.get('page') || '1';
  const query = searchParams.get('q') || '';

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = { page };
        if (query) params.q = query;
        const result = await api.getUserReviews(groupName, userId, params);
        setData(result);
      } catch (err) {
        setError(err.message);
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
      <div className="my-3">
        来自用户{' '}
        <Link to={`/group/${groupName}/user/${data.user_info?.id || userId}`}>
          {data.user_info?.nickname || '用户'}
        </Link>{' '}
        的文献。
      </div>

      {query && (
        <div className="my-3">
          当前搜索：<span className="text-success">{query}</span>
        </div>
      )}

      {!data.reviews || data.reviews.length === 0 ? (
        <div className="my-5 text-center" style={{ minHeight: '200px' }}>
          暂无任何内容。
        </div>
      ) : (
        <>
          <div className="my-3">
            当前共找到 {data.total_count} 篇文献分享
            {data.paginator?.num_pages > 1 &&
              `，本页显示第 ${data.start_index} - ${data.end_index} 篇`
            }
          </div>
          <Pagination paginator={data.paginator} />
          {data.reviews.map((review, idx) => (
            <ReviewCard
              key={review.id}
              review={review}
              index={
                data.indices
                  ? data.indices[idx]
                  : (data.paginator?.start_index || 1) + idx
              }
              groupName={groupName}
            />
          ))}
          <Pagination paginator={data.paginator} />
        </>
      )}
    </section>
  );
}

export default UserReviews;
