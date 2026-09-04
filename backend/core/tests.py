"""Tests for core models."""

from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from config import settings
from core.models import (
    CustomCheckInInterval,
    GroupProfile,
    Journal,
    Label,
    Paper,
    PaperReference,
    PaperTranslation,
    Review,
    UserAlias,
    UserProfile,
    UserSession,
)


class UserProfileModelTest(TestCase):
    def test_create_with_auth_user(self):
        auth_user = User.objects.create_user("alice", "alice@example.com", "pass")
        profile = UserProfile.objects.create(
            auth_user=auth_user, nickname="Alice", wx_openid="wx_alice"
        )
        self.assertEqual(profile.nickname, "Alice")
        self.assertEqual(profile.wx_openid, "wx_alice")
        self.assertFalse(profile.debug_mode)
        self.assertIn("Alice", str(profile))

    def test_create_without_auth_user(self):
        profile = UserProfile.objects.create(nickname="Bob")
        self.assertIsNone(profile.auth_user)
        self.assertEqual(str(profile), "Bob")

    def test_string_representation_with_openid(self):
        profile = UserProfile.objects.create(
            nickname="Charlie", wx_openid="wx_charlie", wx_unionid="union_charlie"
        )
        s = str(profile)
        self.assertIn("Charlie", s)
        self.assertIn("wx_charlie", s)
        self.assertIn("union_charlie", s)


class PaperModelTest(TestCase):
    def test_create_minimal(self):
        paper = Paper.objects.create(title="A Great Paper")
        self.assertEqual(paper.title, "A Great Paper")
        self.assertIsNotNone(paper.create_time)
        self.assertIsNotNone(paper.update_time)

    def test_create_with_full_fields(self):
        paper = Paper.objects.create(
            title="Full Paper",
            journal="Nature",
            journal_abbreviation="Nature",
            pub_date="2024-01-15",
            pub_year=2024,
            authors="Author A\nAuthor B",
            doi="10.1234/test.doi",
            pmid="12345678",
            arxiv_id="2401.00001",
        )
        self.assertEqual(paper.pub_year, 2024)
        self.assertEqual(paper.doi, "10.1234/test.doi")
        self.assertIn("Nature", str(paper))
        self.assertIn("2024", str(paper))

    def test_default_ordering(self):
        p1 = Paper.objects.create(title="First")
        p2 = Paper.objects.create(title="Second")
        papers = Paper.objects.all()
        self.assertEqual(papers[0], p2)  # newest first
        self.assertEqual(papers[1], p1)


class PaperTranslationModelTest(TestCase):
    def test_create_translation(self):
        paper = Paper.objects.create(title="English Title")
        translation = PaperTranslation.objects.create(
            paper=paper, title_cn="中文标题", abstract_cn="中文摘要"
        )
        self.assertEqual(translation.title_cn, "中文标题")
        self.assertEqual(translation.abstract_cn, "中文摘要")


class PaperReferenceModelTest(TestCase):
    def test_create_reference(self):
        paper = Paper.objects.create(title="Main Paper")
        ref = PaperReference.objects.create(
            paper=paper,
            type="ReferenceList",
            ref_type="Reference",
            index=1,
            citation="Author et al. (2024)",
            doi="10.1234/ref.doi",
        )
        self.assertEqual(ref.citation, "Author et al. (2024)")
        self.assertIn("Author", str(ref))


class UserAliasModelTest(TestCase):
    def setUp(self):
        self.user1 = UserProfile.objects.create(nickname="Primary")
        self.user2 = UserProfile.objects.create(nickname="Alias")

    def test_valid_alias(self):
        alias = UserAlias(user=self.user1, alias=self.user2)
        alias.save()
        self.assertEqual(UserAlias.objects.count(), 1)

    def test_self_alias_raises_error(self):
        alias = UserAlias(user=self.user1, alias=self.user1)
        with self.assertRaises(ValidationError):
            alias.save()

    def test_string_representation(self):
        alias = UserAlias(user=self.user1, alias=self.user2)
        alias.save()
        self.assertIn("Primary", str(alias))
        self.assertIn("Alias", str(alias))


class UserSessionModelTest(TestCase):
    def setUp(self):
        self.profile = UserProfile.objects.create(nickname="SessionUser")

    def test_session_creation(self):
        session = UserSession.objects.create(
            user=self.profile,
            session_key="test_key",
            client_type="website",
        )
        self.assertIsNotNone(session.token)
        self.assertIsNotNone(session.expires_at)
        self.assertEqual(session.get_client_type_display(), "网页端")

    def test_session_expiry_default(self):
        session = UserSession.objects.create(
            user=self.profile, session_key="key1", client_type="website"
        )
        expected = timezone.now() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        # Allow a small time delta tolerance
        self.assertAlmostEqual(
            session.expires_at.timestamp(), expected.timestamp(), delta=5
        )

    def test_session_string(self):
        session = UserSession.objects.create(
            user=self.profile, session_key="key1", client_type="weixin"
        )
        self.assertIn("SessionUser", str(session))
        self.assertIn("微信小程序", str(session))


class JournalModelTest(TestCase):
    def test_create_journal(self):
        journal = Journal.objects.create(
            name="Nature",
            abbreviation="Nature",
            impact_factor=50.0,
            impact_factor_year=2024,
            impact_factor_quartile="Q1",
        )
        self.assertEqual(str(journal), "Nature - Nature")
        self.assertEqual(journal.impact_factor_quartile, "Q1")


class LabelModelTest(TestCase):
    def test_create_label(self):
        user = UserProfile.objects.create(nickname="LabelUser")
        label = Label.objects.create(
            user=user, name="important", color="#FF0000", desc="High priority papers"
        )
        self.assertEqual(label.name, "important")
        self.assertEqual(label.color, "#FF0000")


class ReviewModelTest(TestCase):
    def setUp(self):
        self.creator = UserProfile.objects.create(nickname="Reviewer")
        self.paper = Paper.objects.create(title="Reviewed Paper")

    def test_create_review(self):
        review = Review.objects.create(
            paper=self.paper, creator=self.creator, comment="Great paper!"
        )
        self.assertEqual(review.comment, "Great paper!")
        self.assertIn("Reviewer", str(review))
        self.assertIn("Reviewed Paper", str(review))

    def test_review_default_timestamps(self):
        review = Review.objects.create(paper=self.paper, creator=self.creator)
        self.assertIsNotNone(review.checkin_at)
        self.assertIsNotNone(review.update_time)
        self.assertIsNone(review.delete_time)

    def test_review_labels(self):
        review = Review.objects.create(paper=self.paper, creator=self.creator)
        label = Label.objects.create(user=self.creator, name="favorite")
        review.labels.add(label)
        self.assertEqual(review.labels.count(), 1)


class GroupProfileModelTest(TestCase):
    def setUp(self):
        self.member = UserProfile.objects.create(nickname="Member")

    def test_create_group(self):
        group = GroupProfile.objects.create(
            name="testgroup",
            display_name="Test Group",
            desc="A test group",
        )
        self.assertEqual(str(group), "Test Group (testgroup)")

    def test_group_members(self):
        group = GroupProfile.objects.create(name="testgroup", display_name="Test")
        group.members.add(self.member)
        self.assertEqual(group.members.count(), 1)

    def test_group_reviews(self):
        group = GroupProfile.objects.create(name="testgroup", display_name="Test")
        paper = Paper.objects.create(title="Paper")
        creator = UserProfile.objects.create(nickname="Creator")
        review = Review.objects.create(paper=paper, creator=creator)
        group.reviews.add(review)
        self.assertEqual(group.reviews.count(), 1)


class CustomCheckInIntervalModelTest(TestCase):
    def test_create_interval(self):
        interval = CustomCheckInInterval.objects.create(
            year=2024,
            month=6,
            deadline=timezone.now() + timedelta(days=30),
        )
        self.assertEqual(interval.year, 2024)
        self.assertEqual(interval.month, 6)


class MemberReportTest(TestCase):
    """Tests for the member reading-interest report generation."""

    def setUp(self):
        self.group = GroupProfile.objects.create(
            name="xiangma", display_name="响马读paper", desc="a group"
        )
        self.user_a = UserProfile.objects.create(nickname="Alpha")
        self.user_b = UserProfile.objects.create(nickname="Beta")
        self.paper1 = Paper.objects.create(
            title="Deep learning for cancer detection",
            journal="Nature",
            keywords="cancer\ndeep learning\nimaging",
        )
        self.paper2 = Paper.objects.create(
            title="Whole-genome sequencing study",
            journal="Nature Genetics",
            keywords="genome\nsequencing",
        )
        r1 = Review.objects.create(
            paper=self.paper1,
            creator=self.user_a,
            comment="#paper doi:10.1/x Deep learning for cancer detection. "
            "这篇综述非常清晰地梳理了深度学习在癌症检测中的应用。",
        )
        r2 = Review.objects.create(
            paper=self.paper2,
            creator=self.user_a,
            comment="#paper doi:10.2/y Whole-genome sequencing study. "
            "测序方法学部分值得细读。",
        )
        r3 = Review.objects.create(
            paper=self.paper1,
            creator=self.user_b,
            comment="#paper doi:10.3/z Deep learning for cancer detection. "
            "影像组学与深度学习结合是亮点。",
        )
        self.group.reviews.add(r1, r2, r3)

    def test_infer_topics(self):
        from core.member_report import infer_topics

        topics = infer_topics(self.paper1)
        self.assertIn("机器学习 · 深度学习", topics)
        self.assertIn("癌症 · 肿瘤", topics)

    def test_strip_comment_header(self):
        from core.member_report import parse_review_body

        body = parse_review_body(
            "#paper doi:10.1/x Deep learning for cancer detection. 这篇综述非常清晰。"
        )
        self.assertIn("这篇综述非常清晰", body)
        self.assertNotIn("doi:", body)
        self.assertNotIn("Deep learning for cancer detection.", body)

    def test_build_member_profiles(self):
        from core.member_report import build_member_profiles

        profiles = build_member_profiles("xiangma")
        by_name = {p.name: p for p in profiles}
        self.assertIn("Alpha", by_name)
        self.assertIn("Beta", by_name)
        alpha = by_name["Alpha"]
        self.assertEqual(alpha.review_count, 2)
        self.assertGreater(alpha.total_words, 0)
        self.assertIn("机器学习 · 深度学习", alpha.top_topics)

    def test_deterministic_profile_fills_narrative(self):
        from core.member_report import (
            build_member_profiles,
            generate_deterministic_profile,
        )

        profile = build_member_profiles("xiangma")[0]
        generate_deterministic_profile(profile)
        self.assertTrue(profile.portrait)
        self.assertTrue(profile.reading_form)
        self.assertTrue(profile.rating_scale)
        self.assertTrue(profile.theme_entry)

    def test_generate_llm_profile_without_bridge_falls_back(self):
        from core.member_report import (
            build_member_profiles,
            generate_llm_profile,
        )

        profile = build_member_profiles("xiangma")[0]
        # No bridge => deterministic templates, returns False (not LLM-generated).
        used_llm = generate_llm_profile(profile, None)
        self.assertFalse(used_llm)
        self.assertTrue(profile.portrait)
        self.assertTrue(profile.reading_form)

    def test_generate_llm_profile_api_failure_falls_back(self):
        from unittest.mock import MagicMock

        from core.member_report import (
            build_member_profiles,
            generate_llm_profile,
        )

        profile = build_member_profiles("xiangma")[0]
        llm = MagicMock()
        # Simulate an API/network failure (chat_raw returns None).
        llm.chat_raw.return_value = None
        used_llm = generate_llm_profile(profile, llm)
        self.assertFalse(used_llm)
        self.assertTrue(profile.portrait)

    def test_generate_llm_profile_success(self):
        from unittest.mock import MagicMock

        from core.member_report import (
            build_member_profiles,
            generate_llm_profile,
        )

        profile = build_member_profiles("xiangma")[0]
        llm = MagicMock()
        llm.chat_raw.return_value = (
            '{"portrait":"专注方法学的长期思考者",'
            '"reading_form":"以方法学为主的系统型读者",'
            '"rating_scale":"评论细致，偏重方法与证据",'
            '"theme_entry":"可深入方法学新进展"}'
        )
        used_llm = generate_llm_profile(profile, llm)
        self.assertTrue(used_llm)
        self.assertEqual(profile.portrait, "专注方法学的长期思考者")
        self.assertEqual(profile.reading_form, "以方法学为主的系统型读者")

    def test_write_report_creates_json(self):
        import json
        import tempfile

        from django.test import override_settings
        from core.member_report import (
            build_group_aggregate,
            build_member_profiles,
            generate_deterministic_profile,
            write_report,
        )

        profiles = build_member_profiles("xiangma")
        for p in profiles:
            generate_deterministic_profile(p)
        aggregate = build_group_aggregate("xiangma", profiles)

        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(REPORTS_DIR=tmp):
                path = write_report("xiangma", aggregate, profiles)
                self.assertTrue(path.exists())
                self.assertIn("xiangma_member_report.json", path.name)
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(data["group"]["name"], "xiangma")
                self.assertEqual(len(data["members"]), 2)

    def test_member_report_endpoint(self):
        import json
        import tempfile

        from django.test import Client, override_settings
        from core.member_report import (
            build_group_aggregate,
            build_member_profiles,
            generate_deterministic_profile,
            write_report,
        )

        profiles = build_member_profiles("xiangma")
        for p in profiles:
            generate_deterministic_profile(p)
        aggregate = build_group_aggregate("xiangma", profiles)

        c = Client(HTTP_HOST="localhost")
        # Before generation, the endpoint returns 404.
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(REPORTS_DIR=tmp):
                r = c.get("/api/groups/xiangma/member-report/")
                self.assertEqual(r.status_code, 404)

                write_report("xiangma", aggregate, profiles)
                r = c.get("/api/groups/xiangma/member-report/")
                self.assertEqual(r.status_code, 200)
                data = json.loads(r.content)
                self.assertEqual(len(data["members"]), 2)

    def test_member_report_endpoint_group_not_found(self):
        from django.test import Client

        c = Client(HTTP_HOST="localhost")
        r = c.get("/api/groups/nonexistent-group/member-report/")
        self.assertEqual(r.status_code, 404)
