import { useEffect, useState } from "react";
import { useParams } from "react-router";
import api from "../api/client";
import ReviewCard from "../components/ReviewCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { Review } from "../types";

function SingleReview() {
  const { groupName, reviewId } = useParams<{
    groupName: string;
    reviewId: string;
  }>();
  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReview = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await api.getGroupReview<Review>(
          groupName!,
          Number(reviewId),
        );
        setReview(result);
      } catch (err) {
        setError((err as Error).message);
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
        groupName={groupName!}
        showReviewLink={false}
      />
    </div>
  );
}

export default SingleReview;
