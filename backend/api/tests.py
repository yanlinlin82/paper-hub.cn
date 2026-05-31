"""Tests for API views (both frontend API and legacy API)."""

from django.contrib.auth.models import User
from django.test import Client, TestCase

from core.models import GroupProfile, Paper, Review, UserProfile


class FrontendAPITestBase(TestCase):
    """Base class with shared test fixtures for frontend API tests."""

    def setUp(self):
        self.client = Client()

        # Create users
        self.auth_user = User.objects.create_user(
            "testuser", "test@example.com", "password123"
        )
        self.profile = UserProfile.objects.create(
            auth_user=self.auth_user, nickname="Test User"
        )
        self.other_user = User.objects.create_user(
            "otheruser", "other@example.com", "password123"
        )
        self.other_profile = UserProfile.objects.create(
            auth_user=self.other_user, nickname="Other User"
        )

        # Create a group
        self.group = GroupProfile.objects.create(
            name="xiangma", display_name="Xiang Ma", desc="A test group"
        )
        self.group.members.add(self.profile, self.other_profile)

        # Create a paper and review
        self.paper = Paper.objects.create(
            title="Test Paper Title",
            journal="Nature",
            pub_year=2024,
            doi="10.1234/test",
        )
        self.review = Review.objects.create(
            paper=self.paper,
            creator=self.profile,
            comment="A very insightful review.",
        )
        self.group.reviews.add(self.review)


class GetGroupInfoTest(FrontendAPITestBase):
    def test_get_existing_group(self):
        response = self.client.get("/api/groups/xiangma/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "xiangma")
        self.assertEqual(data["display_name"], "Xiang Ma")
        self.assertEqual(data["desc"], "A test group")
        self.assertIn("create_time", data)

    def test_get_nonexistent_group_returns_404(self):
        response = self.client.get("/api/groups/nonexistent/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())


class GetGroupReviewsTest(FrontendAPITestBase):
    def test_get_all_reviews(self):
        response = self.client.get("/api/groups/xiangma/reviews/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reviews", data)
        self.assertIn("paginator", data)
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(len(data["reviews"]), 1)
        self.assertEqual(data["reviews"][0]["paper"]["title"], "Test Paper Title")

    def test_get_all_reviews_default_type(self):
        response = self.client.get("/api/groups/xiangma/reviews/?type=all")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_reviews_nonexistent_group_returns_404(self):
        response = self.client.get("/api/groups/nonexistent/reviews/")
        self.assertEqual(response.status_code, 404)

    def test_reviews_require_auth_for_my_sharing(self):
        response = self.client.get("/api/groups/xiangma/reviews/?type=my_sharing")
        self.assertEqual(response.status_code, 401)

    def test_reviews_require_auth_for_trash(self):
        response = self.client.get("/api/groups/xiangma/reviews/?type=trash")
        self.assertEqual(response.status_code, 401)

    def test_my_sharing_authenticated(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get("/api/groups/xiangma/reviews/?type=my_sharing")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_my_sharing_other_user(self):
        """Other user's my_sharing should see their own reviews (none)."""
        self.client.login(username="otheruser", password="password123")
        response = self.client.get("/api/groups/xiangma/reviews/?type=my_sharing")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 0)

    def test_review_has_paper_info(self):
        response = self.client.get("/api/groups/xiangma/reviews/")
        data = response.json()
        review = data["reviews"][0]
        self.assertEqual(review["paper"]["doi"], "10.1234/test")
        self.assertEqual(review["paper"]["pub_year"], 2024)


class GetSingleReviewTest(FrontendAPITestBase):
    def test_get_single_review(self):
        response = self.client.get(f"/api/groups/xiangma/reviews/{self.review.pk}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # creator info is flat at top level
        self.assertEqual(data["creator_name"], "Test User")
        self.assertEqual(data["creator_id"], self.profile.pk)
        self.assertEqual(data["paper"]["title"], "Test Paper Title")

    def test_get_nonexistent_review_returns_404(self):
        response = self.client.get("/api/groups/xiangma/reviews/99999/")
        self.assertEqual(response.status_code, 404)

    def test_get_nonexistent_group_review_returns_404(self):
        response = self.client.get("/api/groups/nonexistent/reviews/1/")
        self.assertEqual(response.status_code, 404)


class GetCurrentUserTest(FrontendAPITestBase):
    def test_unauthenticated_returns_not_authenticated(self):
        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_authenticated"])

    def test_authenticated_returns_user(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get("/api/me/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_authenticated"])
        self.assertEqual(data["nickname"], "Test User")
        self.assertEqual(data["username"], "testuser")


class LegacyAPITest(TestCase):
    """Basic smoke tests for legacy API endpoints."""

    def setUp(self):
        self.client = Client()
        self.auth_user = User.objects.create_user(
            "legacyuser", "legacy@example.com", "pass"
        )
        self.profile = UserProfile.objects.create(
            auth_user=self.auth_user, nickname="Legacy"
        )

    def test_login_with_get_returns_405(self):
        """Login accepts POST only."""
        response = self.client.get("/api/login")
        self.assertEqual(response.status_code, 405)

    def test_login_with_post_json(self):
        response = self.client.post(
            "/api/login",
            {"username": "legacyuser", "password": "pass"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_search_users_accessible(self):
        response = self.client.get("/api/search-users")
        self.assertEqual(response.status_code, 200)

    def test_username_autocomplete_requires_auth(self):
        """autocomplete requires authentication."""
        response = self.client.get("/api/username-autocomplete")
        self.assertEqual(response.status_code, 401)

    def test_username_autocomplete_with_auth(self):
        self.client.login(username="legacyuser", password="pass")
        response = self.client.get("/api/username-autocomplete")
        self.assertEqual(response.status_code, 200)
