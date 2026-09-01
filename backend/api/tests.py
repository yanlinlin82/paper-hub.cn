"""Tests for API views (both frontend API and legacy API)."""

import json

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.utils import timezone

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


class ReviewDuplicateAndDeleteTest(FrontendAPITestBase):
    """Tests around duplicate review creation and per-review delete/restore."""

    def _post_json(self, url, data):
        return self.client.post(
            url,
            json.dumps(data),
            content_type="application/json",
        )

    def _create_duplicate_reviews(self):
        """Two identical reviews created by `self.profile` sharing one paper."""
        paper = Paper.objects.create(
            title="Duplicate Paper",
            journal="Science",
            doi="10.1000/dup",
        )
        r1 = Review.objects.create(
            paper=paper, creator=self.profile, comment="Same comment"
        )
        r2 = Review.objects.create(
            paper=paper, creator=self.profile, comment="Same comment"
        )
        self.group.reviews.add(r1, r2)
        return paper, r1, r2

    def test_check_in_double_submit_creates_duplicate_reviews(self):
        """Two identical /check-in requests create two reviews on the same paper."""
        self.client.login(username="testuser", password="password123")
        payload = {
            "group_name": "xiangma",
            "paper": {
                "title": "Duplicate Paper",
                "journal": "Science",
                "doi": "10.1000/dup",
                "pub_date": "2024-01-15",
            },
            "comment": "Same comment",
        }
        for _ in range(2):
            resp = self._post_json("/api/check-in", payload)
            self.assertTrue(resp.json()["success"])

        reviews = Review.objects.filter(paper__doi="10.1000/dup", creator=self.profile)
        self.assertEqual(reviews.count(), 2)
        self.assertEqual(reviews[0].paper.pk, reviews[1].paper.pk)

    def test_remove_review_deletes_only_target_review(self):
        """Deleting one review must leave the identical sibling review intact."""
        _, r1, r2 = self._create_duplicate_reviews()
        self.client.login(username="testuser", password="password123")
        resp = self._post_json("/api/new-remove-review", {"review_id": r1.pk})
        self.assertTrue(resp.json()["success"])

        r1.refresh_from_db()
        r2.refresh_from_db()
        self.assertIsNotNone(r1.delete_time)
        self.assertIsNone(r2.delete_time)

    def test_restore_review_clears_delete_time(self):
        """Restoring a review clears its delete_time (pulls it back out of trash)."""
        _, r1, _ = self._create_duplicate_reviews()
        r1.delete_time = timezone.now()
        r1.save()

        self.client.login(username="testuser", password="password123")
        resp = self._post_json("/api/new-restore-review", {"review_id": r1.pk})
        self.assertTrue(resp.json()["success"])

        r1.refresh_from_db()
        self.assertIsNone(r1.delete_time)

    def test_superuser_can_remove_other_users_review(self):
        """A superuser (who sees the delete buttons) may delete any review."""
        review = Review.objects.create(
            paper=self.paper, creator=self.other_profile, comment="other's review"
        )
        self.group.reviews.add(review)

        self.auth_user.is_superuser = True
        self.auth_user.save()
        self.client.login(username="testuser", password="password123")

        resp = self._post_json("/api/new-remove-review", {"review_id": review.pk})
        self.assertTrue(resp.json()["success"])

        review.refresh_from_db()
        self.assertIsNotNone(review.delete_time)

    def test_restore_removes_review_from_group_trash(self):
        """After restore, the review no longer appears in the group trash listing."""
        _, r1, _ = self._create_duplicate_reviews()
        r1.delete_time = timezone.now()
        r1.save()

        self.auth_user.is_superuser = True
        self.auth_user.save()
        self.client.login(username="testuser", password="password123")

        # Before restore the review is in the trash listing.
        trash_before = self.client.get("/api/groups/xiangma/reviews/?type=trash")
        self.assertIn(
            r1.pk, [review["id"] for review in trash_before.json()["reviews"]]
        )

        resp = self._post_json("/api/new-restore-review", {"review_id": r1.pk})
        self.assertTrue(resp.json()["success"])

        # After restore it is no longer listed as trash.
        trash_after = self.client.get("/api/groups/xiangma/reviews/?type=trash")
        self.assertNotIn(
            r1.pk, [review["id"] for review in trash_after.json()["reviews"]]
        )
        r1.refresh_from_db()
        self.assertIsNone(r1.delete_time)


# A raw 32-char CSRF secret: Django compares the (possibly unmasked) header
# token against the cookie secret, and both sides equal this value here.
CSRF_SECRET = "0" * 32


class CsrcTrustedOriginTest(FrontendAPITestBase):
    """CSRF origin checking for the dev frontend behind nginx on :DEV_PORT.

    The SPA is served behind nginx on http://localhost:<DEV_PORT> and the
    browser sends that Origin on every POST. Django's CSRF middleware rejects
    any Origin not in CSRF_TRUSTED_ORIGINS, which is why the trash
    restore/delete buttons failed with a 403 ("Origin checking failed").
    """

    def _post_json_with_origin(self, url, data, origin):
        # nginx forwards Host as `$host` (no port), so Django sees a portless
        # host while the browser Origin carries the full :DEV_PORT. This is the
        # exact condition that triggers the CSRF Origin 403 in the report.
        return self.client.post(
            url,
            json.dumps(data),
            content_type="application/json",
            HTTP_HOST="localhost",
            HTTP_ORIGIN=origin,
            HTTP_X_CSRFTOKEN=CSRF_SECRET,
        )

    def _enable_csrf(self):
        # Client() defaults the *handler* to enforce_csrf_checks=False; set the
        # handler flag so Django actually performs the CSRF origin/token checks.
        self.client.handler.enforce_csrf_checks = True
        self.client.cookies["csrftoken"] = CSRF_SECRET

    def test_remove_review_rejects_untrusted_dev_origin(self):
        """Reproduces the 403: a dev Origin not in CSRF_TRUSTED_ORIGINS is rejected."""
        review = Review.objects.create(
            paper=self.paper, creator=self.profile, comment="x"
        )
        self.group.reviews.add(review)
        self.client.login(username="testuser", password="password123")
        self._enable_csrf()

        resp = self._post_json_with_origin(
            "/api/new-remove-review",
            {"review_id": review.pk},
            "http://localhost:8001",
        )
        self.assertEqual(resp.status_code, 403)

    @override_settings(
        CSRF_TRUSTED_ORIGINS=[
            "http://localhost:5173",
            "http://localhost",
            "http://paper-hub.cn",
            "http://localhost:8001",
        ]
    )
    def test_remove_review_accepts_trusted_dev_origin(self):
        """Once the dev Origin is trusted the same request succeeds."""
        review = Review.objects.create(
            paper=self.paper, creator=self.profile, comment="x"
        )
        self.group.reviews.add(review)
        self.client.login(username="testuser", password="password123")
        self._enable_csrf()

        resp = self._post_json_with_origin(
            "/api/new-remove-review",
            {"review_id": review.pk},
            "http://localhost:8001",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["success"])
