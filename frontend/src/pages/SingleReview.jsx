import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api/client';
import ReviewCard from '../components/ReviewCard';
import LoadingSpinner from '../components/LoadingSpinner';

function SingleReview() {
  const { groupName, reviewId } = useParams();
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReview = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await api.getGroupReview(groupName, reviewId);
        setReview(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchReview();
  }, [groupName, reviewId]);

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!review) return null;

  return (
    <div className="p-2 text-start flex-fill">
      <ReviewCard
        review={review}
        index=""
        groupName={groupName}
        showReviewLink={false}
      />
    </div>
  );
}

export default SingleReview;
