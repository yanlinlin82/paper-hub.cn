"""Member report generation for a reading/paper-sharing group.

This module reads the reviews (paper comments / check-in "打卡") recorded for a
group, aggregates them per member, computes a structured analytic profile for each
member (mirroring the style of a reading-interest report), optionally enriches the
narrative with an LLM, and writes the result to local files.

The report is intentionally data-driven: every field is derived from the review
records (counts, dates, word counts, journals, research topics). The LLM step
only rewrites the narrative to be more readable; everything can be generated without
it via deterministic templates.

Run manually with::

    uv run python manage.py generate_member_report [--group xiangma] [--no-llm]
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from django.conf import settings

# ---------------------------------------------------------------------------
# Research topic taxonomy — maps a paper (by title/keywords/abstract/journal) to
# one or more research fields. Tuned for a bioinformatics / biomedical ML group.
# ---------------------------------------------------------------------------

TOPIC_TAXONOMY: Dict[str, List[str]] = {
    "癌症 · 肿瘤": [
        "cancer",
        "tumor",
        "tumour",
        "carcinoma",
        "oncology",
        "metastasis",
        "neoplasm",
        "pancreatic",
        "glioblastoma",
        "leukemia",
        "lymphoma",
    ],
    "基因组 · 测序": [
        "sequencing",
        "genome",
        "whole-genome",
        "genomic",
        "variant",
        "polymorphism",
        "mutation",
        "methylation",
        "chromatin",
        "epigenom",
        "read alignment",
        "assembl",
    ],
    "单细胞 · 组学": [
        "single-cell",
        "single cell",
        "transcriptom",
        "proteom",
        "metabolom",
        "multi-omic",
        "spatial transcript",
        "scRNA",
        "scATAC",
    ],
    "机器学习 · 深度学习": [
        "deep learning",
        "neural network",
        "convolutional",
        "transformer",
        "machine learning",
        "reinforcement learning",
        "self-supervised",
        "unsupervised",
        "representation learning",
        "regression",
        "classification",
        "clustering",
        "embedding",
        "feature",
        "large language",
        "language model",
    ],
    "医学影像 · 神经": [
        "mri",
        "fmri",
        "neuroimage",
        "brain",
        "cortical",
        "cortex",
        "registration",
        "tractography",
        "fiber",
        "diffusion tensor",
        "imaging",
        "radiomics",
        "segmentation",
    ],
    "蛋白质 · 结构": [
        "protein",
        "structure",
        "fold",
        "docking",
        "binding",
        "amino acid",
        "peptide",
        "leak",
        "RNC",
        "mRNA",
        "proteoform",
    ],
    "免疫 · 微生物": [
        "immune",
        "immunotherapy",
        "t cell",
        "t-cell",
        "tcells",
        "crispr",
        "microbiome",
        "microbiology",
        "bacteri",
        "pathogen",
        "vaccine",
        "antibiotic",
        "car t",
        "cd8",
    ],
    "临床 · 疾病": [
        "clinical",
        "patient",
        "disease",
        "diagnosis",
        "prognosis",
        "treatment",
        "therapy",
        "mortality",
        "survival",
        "biomarker",
        "melanoma",
        "cervical",
        "lung",
        "breast",
        "prostate",
    ],
    "统计 · 方法学": [
        "statistical",
        "bayesian",
        "causal",
        "bias",
        "reproducib",
        "method",
        "model",
        "simulation",
        "benchmark",
        "cross-valid",
        "power",
        "effect size",
        "p-value",
    ],
    "数据 · 数据库 · 工具": [
        "database",
        "tool",
        "web",
        "software",
        "pipeline",
        "platform",
        "dataset",
        "benchmark",
        "repository",
        "workflow",
    ],
    "演化 · 群体遗传": [
        "population",
        "evolution",
        "phylogen",
        "ancestry",
        "admixture",
        "haplotype",
        "natural selection",
        "migration",
        "demographic",
    ],
    "制药 · 药物": [
        "drug",
        "pharmaceutical",
        "screening",
        "compound",
        "small molecule",
        "pharmac",
        "kinase",
        "inhibitor",
    ],
}


# Terms that reveal the *review body* (the part of a comment that is the member's
# own words rather than the pasted paper metadata). Reviews start with a
# "#paper doi:..." header containing DOI/journal/year/title. We strip that header so
# the profile reflects the member's own commentary.
#
# The metadata (DOI / journal / year / paper title) is nearly always Latin script,
# while the member's commentary is Chinese. We use the first CJK character as the
# boundary: everything before the last sentence punctuation that precedes it is
# metadata.
_CJK_FIRST_RE = re.compile(r"[\u4e00-\u9fff]")
_LEADING_PAPER_RE = re.compile(r"^[\s#＃]*(?:paper|paper|文献)\b", re.IGNORECASE)
_LEADING_DOI_RE = re.compile(
    r"^doi\s*[:：]\s*[^\s,，;；。.]+[\s,，;；]*", re.IGNORECASE
)


def strip_comment_header(comment: str) -> str:
    """Remove the '#paper doi:...' metadata header from a review comment.

    Keeps the free-form part of the comment (the member's own words). Falls back
    to the whole comment when no header is detected.
    """
    text = comment or ""
    text = _LEADING_PAPER_RE.sub("", text, count=1).lstrip()
    text = _LEADING_DOI_RE.sub("", text, count=1).lstrip()

    # Boundary = first CJK char (start of the member's own commentary). The
    # metadata header (DOI / journal / year / citation / title) is nearly always
    # Latin script, so drop the whole Latin prefix before the first CJK char.
    m = _CJK_FIRST_RE.search(text)
    if m:
        text = text[m.start() :].strip()
        return text or (comment or "")

    # All-Latin commentary: fall back to removing a leading metadata clause that
    # contains a four-digit year and ends at a sentence boundary.
    m = re.match(r"^([^。\n]{0,160}[,，]\s*(19|20)\d\d[^。\n]{0,120}[。.])", text)
    if m:
        text = text[m.end() :].strip()
    return text or (comment or "")


def infer_topics(paper) -> List[str]:
    """Classify a paper into one or more research topics.

    Uses title, keywords, and abstract text (case-insensitive substring match
    against the taxonomy). Returns the matched topic labels.
    """
    haystack = " \n".join(
        [
            paper.title or "",
            paper.keywords or "",
            paper.abstract or "",
        ]
    ).lower()
    topics = []
    for topic, keywords in TOPIC_TAXONOMY.items():
        if any(kw.lower() in haystack for kw in keywords):
            topics.append(topic)
    return topics


def word_count(text: str) -> int:
    """Count words in a mixed Chinese/English text.

    Chinese characters are counted individually; Latin runs are counted as words.
    """
    if not text:
        return 0
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin_words = len(re.findall(r"[A-Za-z][A-Za-z'\-]*", text))
    return cjk + latin_words


# ---------------------------------------------------------------------------
# Member profile structure
# ---------------------------------------------------------------------------


@dataclass
class MemberProfile:
    user_id: int
    name: str
    review_count: int
    total_words: int
    word_per_review: int
    first_checkin: str
    last_checkin: str
    active_months: int
    top_journals: Dict[str, int]
    top_topics: List[str]
    topic_counts: Dict[str, int]
    reader_type: str
    portrait: str
    reading_form: str
    rating_scale: str
    theme_entry: str
    signature: str = ""
    papers: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "review_count": self.review_count,
            "total_words": self.total_words,
            "word_per_review": self.word_per_review,
            "first_checkin": self.first_checkin,
            "last_checkin": self.last_checkin,
            "active_months": self.active_months,
            "top_journals": self.top_journals,
            "top_topics": self.top_topics,
            "topic_counts": self.topic_counts,
            "reader_type": self.reader_type,
            "portrait": self.portrait,
            "reading_form": self.reading_form,
            "rating_scale": self.rating_scale,
            "theme_entry": self.theme_entry,
            "signature": self.signature,
            "papers": self.papers,
        }


def _member_tier(count: int) -> str:
    """Assign a tier label mirroring the reference report's productivity bands."""
    if count >= 13:
        return "核心"
    if count >= 8:
        return "骨干"
    if count >= 6:
        return "稳定"
    return "活跃"


def _friendly_name(nickname: str) -> str:
    """Collapse WeChat emoji-padded nicknames to a readable label."""
    name = (nickname or "").strip()
    # Drop decorative emoji/symbol runs that flank or pad the name.
    name = re.sub(r"[^\w\u4e00-\u9fff·]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or (nickname or "").strip() or "未命名"


def parse_review_body(comment: str) -> str:
    """Return the member's own prose from a review comment."""
    return strip_comment_header(comment)


# ---------------------------------------------------------------------------
# Data extraction from Django ORM
# ---------------------------------------------------------------------------


def _collect_member_data(reviews) -> Dict[str, List]:
    """Group reviews by canonical member identity.

    Returns a mapping of member name -> list of review dicts. Reviews whose
    creator is an alias (see UserAlias) are merged into their primary profile.
    """
    from core.models import UserAlias

    # Map every user profile id to the canonical (primary) profile id for that person.
    canonical: Dict[int, int] = {}
    for alias in UserAlias.objects.select_related("user", "alias"):
        # alias.alias is the secondary account; alias.user is the primary.
        canonical[alias.alias_id] = alias.user_id

    def resolve(creator_id: int) -> int:
        return canonical.get(creator_id, creator_id)

    grouped: Dict[str, Dict] = defaultdict(
        lambda: {"user_id": None, "nickname": "", "reviews": []}
    )
    for review in reviews:
        creator = review.creator
        creator_id = resolve(creator.pk)
        # A creator with multiple ids sharing the same nickname is the same person
        # even when no explicit alias exists (e.g. re-registrations).
        name = creator.nickname or ""
        bucket = grouped[name]
        bucket["user_id"] = creator_id
        bucket["nickname"] = name
        bucket["reviews"].append(review)
    return grouped


def build_member_profiles(group_name: str, min_count: int = 1) -> List[MemberProfile]:
    """Compute a deterministic MemberProfile for every member of a group."""
    from core.models import GroupProfile, Review

    group = GroupProfile.objects.get(name=group_name)
    reviews = (
        group.reviews.filter(delete_time__isnull=True)
        .select_related("creator", "paper")
        .order_by("checkin_at")
    )

    grouped = _collect_member_data(reviews)

    profiles: List[MemberProfile] = []
    for name, data in grouped.items():
        member_reviews: List = data["reviews"]
        if len(member_reviews) < min_count:
            continue

        total_words = 0
        topic_counter: Counter = Counter()
        journal_counter: Counter = Counter()
        papers = []
        checkins = []
        best_body = ""
        best_paper_title = ""

        for review in member_reviews:
            body = parse_review_body(review.comment)
            total_words += word_count(body)
            checkins.append(review.checkin_at)

            paper = review.paper
            if paper:
                if paper.journal:
                    journal_counter[paper.journal] += 1
                for t in infer_topics(paper):
                    topic_counter[t] += 1
                if len(body) > len(best_body):
                    best_body = body
                    best_paper_title = paper.title or ""
                papers.append(
                    {
                        "id": paper.pk,
                        "review_id": review.pk,
                        "title": paper.title or "",
                        "journal": paper.journal or "",
                        "year": paper.pub_year,
                        "comment_excerpt": body[:400],
                        "checkin_at": review.checkin_at.isoformat(),
                    }
                )

        first = min(checkins).date()
        last = max(checkins).date()
        active_months = max(
            0, (last.year - first.year) * 12 + (last.month - first.month) + 1
        )

        top_topics = [t for t, _ in topic_counter.most_common(4)]
        reader_type = _member_tier(len(member_reviews))
        # Journal label: use the last segment of multi-part journal names.
        top_journals = {
            _shorten_journal(j): c
            for j, c in journal_counter.most_common(5)
            if j
        }
        # Keep papers ordered newest first for the profile view.
        papers.sort(key=lambda p: p["checkin_at"], reverse=True)

        signature = (
            f"「{best_body[:160]}」"
            + (f"——关于《{best_paper_title}》" if best_paper_title else "")
        )

        profiles.append(
            MemberProfile(
                user_id=data["user_id"],
                name=_friendly_name(name),
                review_count=len(member_reviews),
                total_words=total_words,
                word_per_review=(
                    round(total_words / len(member_reviews)) if member_reviews else 0
                ),
                first_checkin=first.isoformat(),
                last_checkin=last.isoformat(),
                active_months=active_months,
                top_journals=top_journals,
                top_topics=top_topics,
                topic_counts=dict(topic_counter),
                reader_type=reader_type,
                portrait="",
                reading_form="",
                rating_scale="",
                theme_entry="",
                signature=signature,
                papers=papers[:8],
            )
        )

    # Sort by review count descending (most prolific first), tie-break by name.
    profiles.sort(key=lambda p: (-p.review_count, p.name))
    return profiles


def _shorten_journal(journal: str) -> str:
    """Shorten a full journal name for display (last segment is most specific)."""
    parts = [p.strip() for p in journal.split(":") if p.strip()]
    if len(parts) >= 2:
        return parts[-1]
    return journal


# ---------------------------------------------------------------------------
# Deterministic narrative generation (no LLM needed)
# ---------------------------------------------------------------------------


def generate_deterministic_profile(profile: MemberProfile) -> MemberProfile:
    """Fill in narrative fields from computed statistics (templates)."""
    topics = "、".join(profile.top_topics) if profile.top_topics else "跨学科"
    journals = "、".join(list(profile.top_journals.keys()))

    if profile.review_count >= 13:
        form = (
            f"高产分享者，{profile.review_count} 条记录集中在 {topics}。"
            f"常投 {journals} 一类期刊，{profile.word_per_review} 字/条，"
            f"评论多以独立观点收束。"
        )
    elif profile.review_count >= 8:
        form = (
            f"稳定输出型读者，专注 {topics}。"
            f"在 {journals} 等方向持续记录，平均每条 {profile.word_per_review} 字。"
        )
    else:
        form = (
            f"侧重主题驱动的读者，当前兴趣偏 {topics}。"
            f"平均每条 {profile.word_per_review} 字，样本较有限。"
        )

    scale = (
        f"共 {profile.review_count} 条评论，总字数 {profile.total_words}，"
        f"活跃跨度 {profile.active_months} 个月（{profile.first_checkin} 至 "
        f"{profile.last_checkin}）。"
    )
    entry = f"可从 {topics} 方向继续深挖；已有 {journals} 等期刊的阅读基础。"

    profile.reading_form = form
    profile.rating_scale = scale
    profile.theme_entry = entry
    profile.portrait = (
        f"兴趣聚焦于 {topics}，属「{profile.reader_type}」型成员。"
    )
    return profile


# ---------------------------------------------------------------------------
# LLM enrichment (OpenAI-compatible). Optional.
# ---------------------------------------------------------------------------


class LLMBridge:
    """Thin wrapper around an OpenAI-compatible chat API (e.g. DeepSeek).

    Enabled only when an API key is available and `use_llm` is True. All calls
    are wrapped in try/except so a failed or missing API never breaks the report.
    Errors are captured in `last_error` so the caller can surface the real
    reason (proxy/network/key) instead of silently reporting "no LLM".
    """

    def __init__(self, base_url: str, api_key: str, model: str, proxy: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.proxy = proxy
        self.last_error: Optional[str] = None

    @classmethod
    def from_settings(cls) -> Optional["LLMBridge"]:
        key = settings.LLM_API_KEY or settings.DEEPSEEK_API_KEY or getattr(
            settings, "OPENAI_API_KEY", ""
        )
        if not key:
            return None
        base_url = getattr(settings, "LLM_BASE_URL", "https://api.deepseek.com")
        proxy = cls._resolve_proxy()
        return cls(
            base_url=base_url,
            api_key=key,
            model=getattr(settings, "LLM_MODEL", "deepseek-chat"),
            proxy=proxy,
        )

    @staticmethod
    def _resolve_proxy() -> Optional[str]:
        """Pick a proxy from LLM_PROXY, else the standard proxy env vars.

        `LLM_NO_PROXY=1` forces a direct connection (handy when the configured
        proxy is dead and the API is directly reachable, e.g. DeepSeek in China).
        """
        import os

        if os.getenv("LLM_NO_PROXY", "") == "1":
            return None
        forced = os.getenv("LLM_PROXY", "")
        if forced:
            return forced
        return os.getenv("HTTPS_PROXY")
    
    def _make_client(self):
        """Build an httpx client with an explicit proxy when configured.

        Returns None when no proxy is set, letting the OpenAI client use its own
        default (env-based) transport. httpx 0.28 accepts a `proxy` URL, e.g.
        socks5://localhost:1090 (requires the `socksio` package, already a dep).
        """
        import httpx

        if self.proxy:
            try:
                return httpx.Client(proxy=self.proxy, timeout=60.0)
            except Exception:
                return None
        return None

    def chat_raw(self, system: str, user: str) -> Optional[str]:
        try:
            from openai import OpenAI
        except Exception as exc:
            self.last_error = f"openai import failed: {exc}"
            return None
        try:
            http_client = self._make_client()
            kwargs = {"base_url": self.base_url, "api_key": self.api_key}
            if http_client is not None:
                kwargs["http_client"] = http_client
            client = OpenAI(**kwargs)
            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.4,
                max_tokens=600,
            )
            return resp.choices[0].message.content or ""
        except Exception as exc:
            self.last_error = str(exc)
            return None


def generate_llm_profile(profile: MemberProfile, llm: Optional[LLMBridge]) -> bool:
    """Rewrite a single member's narrative with the LLM; fall back to templates.

    Returns True if the LLM narrative was applied, False if it fell back to
    deterministic templates (e.g. no bridge, network/API failure). The caller uses
    this to record an honest `generator.mode`.
    """
    if not llm:
        generate_deterministic_profile(profile)
        return False

    reviews_txt = []
    for p in profile.papers:
        reviews_txt.append(
            f"- 《{p['title']}》({p['journal'] or p['year'] or ''}): "
            f"{p['comment_excerpt'] or '（无评语）'}"
        )
    paper_list = "\n".join(reviews_txt) if reviews_txt else "（该成员暂无具体论文）"

    system = (
        "你是一个学术社群数据分析师，为一名持续打卡阅读学术论文的成员撰写"
        "「读者画像」。请只依据提供的真实资料，用中文输出，简洁克制、具体而准确，"
        "不要编造资料中不存在的论文、期刊或数据。"
    )
    user = (
        f"成员：{profile.name}\n"
        f"记录：{profile.review_count} 条，每条平均 {profile.word_per_review} 字，"
        f"总字数 {profile.total_words}，活跃 {profile.active_months} 个月"
        f"（{profile.first_checkin} 至 {profile.last_checkin}）。\n"
        f"聚焦方向：{'、'.join(profile.top_topics) or '跨学科'}。\n"
        f"常投期刊：{'、'.join(profile.top_journals.keys()) or '—'}。\n"
        f"代表评论：\n{paper_list}\n\n"
        f"请按以下 JSON 输出（严格 JSON，不要多余文字）：\n"
        f"{{"
        f'"portrait":"一句话概括他/她的阅读画像",'
        f'"reading_form":"描述他/她主要读什么、怎么选论文（选文形态）",'
        f'"rating_scale":"描述他/她的评论深度与关注点（评分标尺/评论习惯）",'
        f'"theme_entry":"给出一个适合他/她的下一步阅读主题方向"'
        f"}}"
    )
    result = llm.chat_raw(system, user)
    if not result:
        generate_deterministic_profile(profile)
        return False

    # Best-effort JSON parse; fall back to templates on failure.
    try:
        m = re.search(r"\{.*\}", result, re.DOTALL)
        data = json.loads(m.group(0)) if m else None
    except Exception:
        data = None
    if not data:
        generate_deterministic_profile(profile)
        return False

    portrait = data.get("portrait", "")
    reading_form = data.get("reading_form", "")
    rating_scale = data.get("rating_scale", "")
    theme_entry = data.get("theme_entry", "")
    # Only count as LLM-generated if the model supplied all four core fields.
    if all([portrait, reading_form, rating_scale, theme_entry]):
        profile.portrait = portrait
        profile.reading_form = reading_form
        profile.rating_scale = rating_scale
        profile.theme_entry = theme_entry
        return True

    # Partial/missing fields -> fill with templates; do not claim full LLM output.
    profile.portrait = portrait
    profile.reading_form = reading_form
    profile.rating_scale = rating_scale
    profile.theme_entry = theme_entry
    generate_deterministic_profile(profile)
    return False


# ---------------------------------------------------------------------------
# Group-level aggregate
# ---------------------------------------------------------------------------


def build_common_papers(group_name: str, min_readers: int = 2, limit: int = 10) -> List[Dict]:
    """Find papers read by multiple distinct members.

    Returns papers ordered by number of distinct readers, each with a summary of
    who read it and one clickable review id.
    """
    from core.models import GroupProfile

    group = GroupProfile.objects.get(name=group_name)
    reviews = (
        group.reviews.filter(delete_time__isnull=True)
        .select_related("creator", "paper")
        .order_by("checkin_at")
    )

    by_paper: Dict[int, Dict] = defaultdict(
        lambda: {"title": "", "journal": "", "year": None, "readers": []}
    )
    seen_reader: Dict[int, int] = {}  # (paper_id, user_id) => reader index
    for review in reviews:
        paper = review.paper
        if not paper:
            continue
        entry = by_paper[paper.pk]
        entry["title"] = paper.title or ""
        entry["journal"] = paper.journal or ""
        entry["year"] = paper.pub_year
        entry["review_id"] = review.pk  # last one wins; useful as a link target
        uid = review.creator.pk
        key = (paper.pk, uid)
        if key not in seen_reader:
            seen_reader[key] = len(entry["readers"])
            entry["readers"].append(
                {"user_id": uid, "name": _friendly_name(review.creator.nickname)}
            )

    common = []
    for paper_id, entry in by_paper.items():
        readers = entry["readers"]
        if len(readers) < min_readers:
            continue
        common.append(
            {
                "paper_id": paper_id,
                "review_id": entry.get("review_id"),
                "title": entry["title"],
                "journal": _shorten_journal(entry["journal"]),
                "year": entry["year"],
                "reader_count": len(readers),
                "readers": readers[:12],
            }
        )
    common.sort(key=lambda c: (-c["reader_count"], c["title"]))
    return common[:limit]


def build_cohort_summary(aggregate: Dict, profiles: Sequence[MemberProfile]) -> str:
    """One-sentence, playful-but-factual summary of the group's reading profile."""
    if not profiles:
        return ""
    top_axis = aggregate["topic_axes"][0] if aggregate["topic_axes"] else None
    axis_txt = top_axis["topic"] if top_axis else "跨学科"
    return (
        f"这份报告汇总了 {aggregate['total_reviews']} 条论文简评、"
        f"约 {aggregate['total_words'] / 10000:.1f} 万字。"
        f"其中「{axis_txt}」是出现最多的方向，命中 "
        f"{top_axis['pct'] if top_axis else 0}% 的记录。"
    )


def build_observations(aggregate: Dict, profiles: Sequence[MemberProfile]) -> List[Dict]:
    """A few concise, factual observations about the sharing records.

    Every claim is derived from the computed aggregate data; no individual
    member is singled out and the wording stays restrained.
    """
    if not profiles:
        return []

    obs = []
    top_axis = aggregate["topic_axes"][0] if aggregate["topic_axes"] else None
    if top_axis:
        obs.append(
            {
                "title": "关注最集中的方向",
                "text": (
                    f"「{top_axis['topic']}」命中率最高（{top_axis['pct']}%），"
                    "是分享记录里出现最多的研究方向。"
                ),
            }
        )

    top_journal = list(aggregate["top_journals"].items())
    if top_journal:
        name, count = top_journal[0]
        obs.append(
            {
                "title": "出现最多的来源",
                "text": f"{name} 是被分享最多次的期刊，共 {count} 次。",
            }
        )

    avg_words = (
        aggregate["total_words"] / aggregate["total_reviews"]
        if aggregate["total_reviews"]
        else 0
    )
    obs.append(
        {
            "title": "平均篇幅",
            "text": f"平均每条简评 {avg_words:.0f} 字。",
        }
    )

    tiers = aggregate["member_tiers"]
    core = tiers.get("核心", 0)
    if core:
        obs.append(
            {
                "title": "长期分享者",
                "text": f"累计分享 13 条及以上（「核心」档）的有 {core} 位。",
            }
        )

    if aggregate.get("common_papers"):
        top_common = aggregate["common_papers"][0]
        obs.append(
            {
                "title": "被多人读过的论文",
                "text": (
                    f"《{top_common['title'][:40]}》共有 {top_common['reader_count']} 位"
                    "分享者先后读过。"
                ),
            }
        )

    return obs


def build_group_aggregate(group_name: str, profiles: Sequence[MemberProfile]) -> Dict:
    """Compute group-level aggregates plus cohort narrative (summaries/observations)."""
    total_reviews = sum(p.review_count for p in profiles)
    total_words = sum(p.total_words for p in profiles)
    axis_counter: Counter = Counter()
    journal_counter: Counter = Counter()
    for p in profiles:
        for t, c in p.topic_counts.items():
            axis_counter[t] += c
        for j, c in p.top_journals.items():
            journal_counter[j] += c

    axis_rows = []
    for topic, count in axis_counter.most_common():
        axis_rows.append(
            {
                "topic": topic,
                "count": count,
                "pct": round(count / total_reviews * 100, 1) if total_reviews else 0,
            }
        )

    tiers: Counter = Counter(p.reader_type for p in profiles)
    aggregate = {
        "total_reviews": total_reviews,
        "total_members": len(profiles),
        "total_words": total_words,
        "top_journals": {
            j: c for j, c in journal_counter.most_common(8)
        },
        "topic_axes": axis_rows,
        "member_tiers": {t: tiers[t] for t in ["核心", "骨干", "稳定", "活跃"]},
    }
    # Cohort narrative: a one-line summary, factual observations, and the
    # papers read by the most distinct members. common_papers must be set before
    # build_observations so that observation can reference it.
    aggregate["common_papers"] = build_common_papers(group_name)
    aggregate["cohort_summary"] = build_cohort_summary(aggregate, profiles)
    aggregate["observations"] = build_observations(aggregate, profiles)
    return aggregate


# ---------------------------------------------------------------------------
# Persistence (local files)
# ---------------------------------------------------------------------------


def write_report(
    group_name: str,
    aggregate: Dict,
    profiles: List[MemberProfile],
    generator: Optional[Dict] = None,
) -> Path:
    """Write the JSON report to `backend/reports/` and return its path.

    The file is the single source of truth consumed by the website API endpoint.
    """
    from core.models import GroupProfile

    group = GroupProfile.objects.get(name=group_name)
    report = {
        "group": {
            "name": group.name,
            "display_name": group.display_name,
            "desc": group.desc,
        },
        "generated_at": datetime.now().astimezone().isoformat(),
        "generator": generator or {"mode": "rule", "provider": "rule", "model": ""},
        "aggregate": aggregate,
        "members": [p.to_dict() for p in profiles],
    }
    out_dir = Path(settings.REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{group_name}_member_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), "utf-8")
    return path


def _esc(text) -> str:
    """Escape text for safe inline HTML output."""
    from html import escape

    return escape(text or "", quote=True)


def build_html_report(
    group_name: str,
    aggregate: Dict,
    profiles: List[MemberProfile],
    site_prefix: str = "/",
    generator: Optional[Dict] = None,
) -> str:
    """Render a self-contained HTML report (mirrors the reference report style).

    Each member card links to the website's per-member review page so the report
    can be shared or opened directly while still reaching the clickable profiles.
    """
    from core.models import GroupProfile

    group = GroupProfile.objects.get(name=group_name)
    prefix = (site_prefix or "/").rstrip("/") + "/group/" + group_name

    fig_members = len(profiles)
    total_reviews = aggregate["total_reviews"]
    total_words = aggregate["total_words"]
    max_topic = max(1, max((a["count"] for a in aggregate["topic_axes"]), default=0))
    max_journal = max(1, max(aggregate["top_journals"].values(), default=0))

    bars = []
    for axis in aggregate["topic_axes"]:
        w = round(axis["count"] / max_topic * 100, 1)
        bars.append(
            f'<div class="bar"><span class="bl">{_esc(axis["topic"])}</span>'
            f'<span class="bt"><span class="bf" style="width:{w}%"></span></span>'
            f'<span class="bv">{axis["count"]} · {axis["pct"]}%</span></div>'
        )

    journals = []
    for name, count in list(aggregate["top_journals"].items())[:8]:
        w = round(count / max_journal * 100, 1)
        journals.append(
            f'<div class="bar"><span class="bl">{_esc(name)}</span>'
            f'<span class="bt"><span class="bf weak" style="width:{w}%"></span></span>'
            f'<span class="bv">{count}</span></div>'
        )

    member_cards = []
    for p in profiles:
        topics = " · ".join(p.top_topics[:4]) or "跨学科"
        journal_links = []
        for j, _c in p.top_journals.items():
            journal_links.append(
                f'<a href="{prefix}/journal/{_esc(j)}">{_esc(j)}</a>'
            )
        journals_txt = "、".join(journal_links) or "—"
        papers = "".join(
            f'<li>'
            f'<a class="bt2" href="{prefix}/review/{pp.get("review_id")}">{_esc(pp["title"])}</a>'
            f'<span class="bm"> · '
            f'<a href="{prefix}/journal/{_esc(pp.get("journal") or "")}">{_esc(pp.get("journal") or "")}</a>'
            f'{_esc(str(pp.get("year") or ""))}</span>'
            f'<div class="bw">{_esc(pp.get("comment_excerpt") or "")[:220]}</div></li>'
            for pp in p.papers[:5]
        ) or "<li>暂无代表评论</li>"
        member_cards.append(
            f'<div class="m">'
            f'<div class="mh"><a class="mn" href="{prefix}/user/{p.user_id}">{_esc(p.name)}</a>'
            f'<span class="mb {_tier_class(p.reader_type)}">{_esc(p.reader_type)}</span>'
            f'<span class="mt">{p.review_count} 条 · {p.word_per_review} 字/条</span></div>'
            f'<div class="axes">{_esc(topics)}</div>'
            f'<dl><dt>选文形态</dt><dd>{_esc(p.reading_form)}</dd>'
            f'<dt>评论深度与关注点</dt><dd>{_esc(p.rating_scale)}</dd>'
            f'<dt>下一步主题入口</dt><dd>{_esc(p.theme_entry)}</dd>'
            f'<dt>常投期刊</dt><dd>{journals_txt}</dd></dl>'
            f'<div class="books">{papers}</div>'
            f'</div>'
        )

    tiers = []
    for t in ["核心", "骨干", "稳定", "活跃"]:
        c = aggregate["member_tiers"].get(t, 0)
        tiers.append(f'<span class="mb {_tier_class(t)}">{_esc(t)} {c}</span>')

    # Cohort narrative: summary + fun observations + commonly-read papers.
    cohort_summary = _esc(aggregate.get("cohort_summary", ""))
    observations_html = "".join(
        f'<li><b>{_esc(o.get("title", ""))}：</b>{_esc(o.get("text", ""))}</li>'
        for o in aggregate.get("observations", [])
    )
    common_html = []
    for cp in aggregate.get("common_papers", []):
        readers = "、".join(
            f'<a href="{prefix}/user/{r["user_id"]}">{_esc(r["name"])}</a>'
            for r in cp["readers"]
        )
        common_html.append(
            f'<li><a class="bt2" href="{prefix}/review/{cp.get("review_id")}">'
            f'{_esc(cp["title"])}</a>'
            f'<span class="bm"> · {_esc(cp["journal"])} {_esc(str(cp.get("year") or ""))}'
            f' · {cp["reader_count"]} 人读过</span>'
            f'<div class="bw">{readers}</div></li>'
        )
    common_html = "".join(common_html)

    # AI model attribution.
    gen = generator or {}
    if gen.get("mode") == "llm" and gen.get("model"):
        gen_html = (
            f'· 由 <b>{_esc(gen.get("provider", ""))}</b> 大模型 '
            f'({_esc(gen.get("model", ""))}) 生成')
    else:
        gen_html = "· 由本地统计规则生成（未调用大模型）"

    now = datetime.now().strftime("%Y-%m-%d")
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(group.display_name)} · 成员阅读画像</title>
<style>
:root{{--ac:#1f6f5c;--ac2:#7fb3a3;--ink:#1f2622;--ink2:#4b5563;--muted:#8a94a6;--line:#e4e7e4;--card:#fff;}}
*{{box-sizing:border-box}}body{{margin:0;background:#f6f7f6;color:var(--ink);
font-family:"PingFang SC","Microsoft YaHei",sans-serif;font-size:15px;line-height:1.85}}
.wrap{{max-width:940px;margin:0 auto;padding:44px 24px 70px}}
.hd{{border-bottom:2px solid var(--ink);padding-bottom:18px;margin-bottom:30px}}
.kicker{{font-size:11px;letter-spacing:.28em;color:var(--ac);margin:0 0 10px}}
h1{{font-size:27px;margin:0 0 8px}}h2{{font-size:19px;margin:40px 0 6px;
border-bottom:1px solid var(--line);padding-bottom:8px}}
.figs{{display:flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:4px;overflow:hidden}}
.fig{{flex:1 1 130px;padding:14px 16px;border-right:1px solid var(--line)}}
.fig:last-child{{border-right:0}}.fig b{{display:block;font-size:22px;color:var(--ac)}}
.fig span{{font-size:11.5px;color:var(--muted)}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:18px 20px;margin:14px 0}}
.summary{{border-left:3px solid var(--ac);background:#f4f8f6;padding:16px 18px;margin:14px 0;font-size:14px;color:var(--ink2)}}
.bar{{display:flex;align-items:center;font-size:13px;margin:6px 0}}
.bl{{width:130px;flex:0 0 130px;color:var(--ink2)}}
.bt{{flex:1;height:14px;background:#eef1ef;border-radius:2px;overflow:hidden}}
.bf{{display:block;height:100%;background:var(--ac);border-radius:2px;min-width:2px}}
.bf.weak{{background:var(--ac2)}}.bv{{width:80px;flex:0 0 80px;text-align:right;color:var(--muted);font-size:12px}}
.mgrid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}}
.m{{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:13px 16px}}
.mh{{display:flex;align-items:baseline;gap:7px;flex-wrap:wrap;border-bottom:1px dashed var(--line);padding-bottom:6px;margin-bottom:8px}}
.mn{{font-size:15px;font-weight:700;color:var(--ink);text-decoration:none}}
.mn:hover{{color:var(--ac)}}.mt{{margin-left:auto;font-size:11.5px;color:var(--muted)}}
.mb{{font-size:10.5px;border-radius:2px;padding:1px 6px}}
.mb.a{{color:var(--ac);background:#e8f1ed}}.mb.b{{color:#5b6b66;background:#eef1ef}}
.mb.c{{color:#c99a34;background:#fbf5e6}}.mb.d{{color:#8c2f39;background:#faf0ef}}
.axes{{font-size:12px;color:var(--ac);margin-bottom:2px}}
dl{{margin:0}}dt{{font-size:11px;color:var(--muted);margin-top:8px}}
dd{{margin:1px 0 0;font-size:13px;color:var(--ink2);line-height:1.7}}
dd a{{color:var(--ac)}}
.books{{list-style:none;padding:0;margin:10px 0 0;counter-reset:b}}
.books li{{counter-increment:b;padding:8px 0 8px 26px;position:relative;border-bottom:1px dashed var(--line);font-size:13px}}
.books li:last-child{{border-bottom:0}}.books li::before{{content:counter(b,decimal-leading-zero);position:absolute;left:0;font-size:11px;color:var(--ac2)}}
.bt2{{font-weight:700;color:var(--ink);text-decoration:none}}.bt2:hover{{color:var(--ac)}}
.bm{{color:var(--muted);font-size:12px}}.bm a{{color:var(--ac);text-decoration:none}}
.bw{{color:var(--ink2);margin-top:2px}}
footer{{margin-top:44px;padding-top:14px;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}}
@media(max-width:700px){{.mgrid{{grid-template-columns:1fr}}.bl{{width:96px;flex:0 0 96px;font-size:12px}}}}
</style></head><body><div class="wrap">
<header class="hd"><p class="kicker">MEMBER REVIEW PROFILE</p>
<h1>{_esc(group.display_name)} · 成员阅读画像</h1>
<p>基于 {total_reviews} 条论文分享记录（累计 {fig_members} 位分享者，生成于 {now}）。</p>
<p style="font-size:12.5px;color:var(--muted)">{gen_html}</p></header>

<div class="figs">
<div class="fig"><b>{total_reviews}</b><span>分享记录</span></div>
<div class="fig"><b>{fig_members}</b><span>打卡成员</span></div>
<div class="fig"><b>{round(total_words / 10000, 1)} 万</b><span>累计简评字数</span></div>
</div>

<div class="summary"><b>概览：</b>{cohort_summary}</div>

<h2>研究主题轴</h2><div class="card">{''.join(bars)}</div>

<h2>常读期刊</h2><div class="card">{''.join(journals)}</div>

<h2>成员分层</h2><div class="card">{' '.join(tiers)}</div>

<h2>数据观察</h2><div class="card"><ol style="margin:0;padding-left:20px">{observations_html}</ol></div>

<h2>共同阅读 · 被多人分享的论文</h2>
<p class="lead" style="color:var(--ink2);font-size:13px;margin:6px 0 0">被多位分享者先后读过的同一篇论文。</p>
<div class="card"><ul class="books">{common_html or '<li>暂无同一篇被多人阅读的记录</li>'}</ul></div>

<h2>历年分享者逐一画像</h2>
<p class="lead" style="color:var(--ink2);font-size:14px">点击分享者姓名可跳转到网站查看 TA 的完整评价画像。</p>
<div class="mgrid">{''.join(member_cards)}</div>

<footer>由 paper-hub.cn 生成的报告 · {gen_html}<br>点击成员姓名、期刊名或论文标题均可跳转到网站对应页面。</footer>
</div></body></html>"""
    return html


def _tier_class(tier: str) -> str:
    return {"核心": "a", "骨干": "b", "稳定": "c", "活跃": "d"}.get(tier, "b")


def write_html_report(
    group_name: str,
    aggregate: Dict,
    profiles: List[MemberProfile],
    generator: Optional[Dict] = None,
) -> Path:
    """Write the standalone HTML report next to the JSON report."""
    html = build_html_report(group_name, aggregate, profiles, generator=generator)
    out_dir = Path(settings.REPORTS_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{group_name}_member_report.html"
    path.write_text(html, "utf-8")
    return path
