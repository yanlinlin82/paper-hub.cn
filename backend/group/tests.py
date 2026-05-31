"""Tests for group views (legacy SPA redirects)."""

from django.test import Client, TestCase


class GroupRedirectTest(TestCase):
    """Group pages redirect to the React SPA URLs."""

    def setUp(self):
        self.client = Client()

    def test_index_redirects_to_spa(self):
        response = self.client.get("/group/testgroup/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup", response.url)

    def test_all_page_redirects(self):
        response = self.client.get("/group/testgroup/all")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/all", response.url)

    def test_my_sharing_redirects(self):
        response = self.client.get("/group/testgroup/my_sharing")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/my_sharing", response.url)

    def test_recent_redirects(self):
        response = self.client.get("/group/testgroup/recent")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/recent", response.url)

    def test_this_month_redirects(self):
        response = self.client.get("/group/testgroup/this_month")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/this_month", response.url)

    def test_last_month_redirects(self):
        response = self.client.get("/group/testgroup/last_month")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/last_month", response.url)

    def test_trash_redirects(self):
        response = self.client.get("/group/testgroup/trash")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/trash", response.url)

    def test_single_review_redirects(self):
        response = self.client.get("/group/testgroup/review/42")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/review/42", response.url)

    def test_user_page_redirects(self):
        response = self.client.get("/group/testgroup/user/1")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/user/1", response.url)

    def test_journal_page_redirects(self):
        response = self.client.get("/group/testgroup/journal/Nature")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/journal/Nature", response.url)

    def test_rank_page_redirects(self):
        response = self.client.get("/group/testgroup/rank")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/rank", response.url)

    def test_rank_type_page_redirects(self):
        response = self.client.get("/group/testgroup/rank/this_month")
        self.assertEqual(response.status_code, 302)
        self.assertIn("group/testgroup/rank/this_month", response.url)
