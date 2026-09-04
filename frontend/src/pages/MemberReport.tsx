import { useEffect, useState } from "react";
import { useParams, Link } from "react-router";
import Modal from "react-bootstrap/Modal";
import api from "../api/client";
import LoadingSpinner from "../components/LoadingSpinner";
import {
  CommonPaper,
  MemberProfile,
  MemberReport,
  TopicAxis,
} from "../types";

const TIER_CLASS: Record<string, string> = {
  核心: "tier-a",
  骨干: "tier-b",
  稳定: "tier-c",
  活跃: "tier-d",
};

function formatDate(iso: string | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return "";
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

function TopicBars({ axes }: { axes: TopicAxis[] }) {
  const max = Math.max(1, ...axes.map((a) => a.count));
  return (
    <div className="report-bars">
      {axes.map((axis) => (
        <div key={axis.topic} className="report-bar">
          <span className="report-bar-label" title={axis.topic}>
            {axis.topic}
          </span>
          <span className="report-bar-track">
            <span
              className="report-bar-fill"
              style={{ width: `${(axis.count / max) * 100}%` }}
            />
          </span>
          <span className="report-bar-value">
            {axis.count} · {axis.pct}%
          </span>
        </div>
      ))}
    </div>
  );
}

function formatWordCount(n: number): string {
  if (n >= 10000) return `${(n / 10000).toFixed(1)} 万`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)} 千`;
  return `${n}`;
}

function GeneratorCredit({
  generator,
}: {
  generator: MemberReport["generator"] | null | undefined;
}) {
  if (!generator) return null;
  if (generator.mode === "llm" && generator.model) {
    return (
      <span className="report-credit">
        由 <b>{generator.provider}</b> 大模型 ({generator.model}) 生成
      </span>
    );
  }
  return (
    <span className="report-credit">
      由本地统计规则生成（未调用大模型）
    </span>
  );
}

function MemberProfileModal({
  profile,
  groupName,
  onClose,
}: {
  profile: MemberProfile | null;
  groupName: string;
  onClose: () => void;
}) {
  const journals = profile
    ? Object.entries(profile.top_journals)
    : [];
  const maxJournal = Math.max(1, ...journals.map(([, c]) => c));

  return (
    <Modal show={!!profile} onHide={onClose} size="lg" centered scrollable>
      <Modal.Header closeButton>
        <Modal.Title>
          {profile && (
            <>
              <span className="me-2">{profile.name}</span>
              <span
                className={`report-tier ${TIER_CLASS[profile.reader_type] ?? ""}`}
              >
                {profile.reader_type}
              </span>
            </>
          )}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {profile && (
          <>
            {/* Hero: stats + intro */}
            <div className="report-profile-hero">
              <div className="report-stat-grid">
                <div className="report-stat">
                  <b>{profile.review_count}</b>
                  <span>分享条数</span>
                </div>
                <div className="report-stat">
                  <b>{profile.word_per_review}</b>
                  <span>字/条</span>
                </div>
                <div className="report-stat">
                  <b>{formatWordCount(profile.total_words)}</b>
                  <span>总字数</span>
                </div>
                <div className="report-stat">
                  <b>{profile.active_months}</b>
                  <span>活跃月数</span>
                </div>
              </div>
              <div className="text-body-secondary small mt-2">
                {formatDate(profile.first_checkin)} 至 {formatDate(profile.last_checkin)}
              </div>
              {profile.portrait && (
                <p className="report-quote mt-3 mb-0">{profile.portrait}</p>
              )}
            </div>

            {/* Profile narrative */}
            <div className="report-modal-section">
              <div className="report-modal-row">
                <span className="report-label">选文形态</span>
                <p className="report-value">{profile.reading_form || "暂无"}</p>
              </div>
              <div className="report-modal-row">
                <span className="report-label">评论深度与关注点</span>
                <p className="report-value">{profile.rating_scale || "暂无"}</p>
              </div>
              <div className="report-modal-row">
                <span className="report-label">下一步主题入口</span>
                <p className="report-value">{profile.theme_entry || "暂无"}</p>
              </div>
            </div>

            {/* Research preferences */}
            {(journals.length > 0 || profile.top_topics.length > 0) && (
              <div className="report-modal-section">
                {journals.length > 0 && (
                  <div className="report-modal-block">
                    <span className="report-label">常投期刊</span>
                    <div className="report-journals">
                      {journals.map(([name, count]) => (
                        <span key={name} className="report-journal">
                          <span
                            className="report-journal-bar"
                            style={{ width: `${(count / maxJournal) * 100}%` }}
                          />
                          <Link
                            to={`/group/${groupName}/journal/${encodeURIComponent(name)}`}
                            className="report-journal-name"
                          >
                            {name}
                          </Link>
                          <span className="report-journal-count">{count}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {profile.top_topics.length > 0 && (
                  <div className="report-modal-block">
                    <span className="report-label">聚焦方向</span>
                    <div className="d-flex flex-wrap gap-2">
                      {profile.top_topics.map((topic) => (
                        <span key={topic} className="badge report-topic">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Signature */}
            {profile.signature && (
              <div className="report-modal-section">
                <span className="report-label">一句话评论</span>
                <blockquote className="report-quote report-quote-block">
                  {profile.signature}
                </blockquote>
              </div>
            )}

            {/* Representative papers */}
            {profile.papers.length > 0 && (
              <div className="report-modal-section">
                <div className="d-flex align-items-center justify-content-between">
                  <span className="report-label">代表评论</span>
                  <Link
                    to={`/group/${groupName}/user/${profile.user_id}`}
                    className="text-body-secondary small"
                    onClick={onClose}
                  >
                    共 {profile.review_count} 条，查看全部 →
                  </Link>
                </div>
                <ul className="list-unstyled report-papers">
                  {profile.papers.slice(0, 5).map((p) => (
                    <li key={p.id} className="report-paper">
                      <div className="report-paper-title">
                        <Link
                          to={`/group/${groupName}/review/${p.review_id}`}
                          className="report-paper-link"
                        >
                          {p.title || "（无标题）"}
                        </Link>
                        {p.journal && (
                          <Link
                            to={`/group/${groupName}/journal/${encodeURIComponent(p.journal)}`}
                            className="text-body-secondary small ms-1"
                          >
                            {p.journal}
                            {p.year ? ` (${p.year})` : ""}
                          </Link>
                        )}
                      </div>
                      {p.comment_excerpt && (
                        <div className="report-paper-comment">
                          {p.comment_excerpt}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Footer actions */}
            <div className="d-flex flex-wrap gap-2 mt-3">
              <Link
                to={`/group/${groupName}/user/${profile.user_id}`}
                className="btn btn-outline-primary btn-sm"
                onClick={onClose}
              >
                查看 TA 的全部分享 →
              </Link>
              <Link
                to={`/group/${groupName}/rank`}
                className="btn btn-outline-secondary btn-sm"
                onClick={onClose}
              >
                社群榜单 →
              </Link>
            </div>
          </>
        )}
      </Modal.Body>
    </Modal>
  );
}

function MemberReportPage() {
  const { groupName } = useParams<{ groupName: string }>();
  const [report, setReport] = useState<MemberReport | null>(null);
  const [selected, setSelected] = useState<MemberProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await api.getMemberReport<MemberReport>(groupName!);
        setReport(result);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [groupName]);

  if (loading) return <LoadingSpinner />;
  if (error)
    return (
      <div className="alert alert-danger">
        {error}
        <div className="mt-2 small">
          提示：请先在服务器运行{" "}
          <code>uv run python manage.py generate_member_report --group {groupName}</code>{" "}
          生成报告。
        </div>
      </div>
    );
  if (!report) return null;

  const { group, aggregate, members } = report;

  return (
    <section className="member-report">
      <header className="report-header mb-4">
        <span className="report-kicker">MEMBER REVIEW PROFILE</span>
        <h1 className="h3 mb-1">{group.display_name} · 成员阅读画像</h1>
        <p className="text-body-secondary small mb-1">
          基于 {aggregate.total_reviews} 条论文分享记录（累计 {aggregate.total_members} 位分享者）。
          <span className="ms-2">生成于 {formatDate(report.generated_at)}</span>
        </p>
        <div className="d-flex flex-wrap align-items-center gap-3">
          <GeneratorCredit generator={report.generator} />
          <span className="report-header-links">
            <Link to={`/group/${groupName}/rank`}>社群榜单</Link>
            <Link to={`/group/${groupName}/all`}>所有分享</Link>
            <Link to={`/group/${groupName}`}>社群首页</Link>
          </span>
        </div>
      </header>

      {/* Aggregate stat cards */}
      <div className="report-figs mb-4">
        <div className="report-fig">
          <b>{aggregate.total_reviews}</b>
          <span>分享记录</span>
        </div>
        <div className="report-fig">
          <b>{aggregate.total_members}</b>
          <span>打卡成员</span>
        </div>
        <div className="report-fig">
          <b>{formatWordCount(aggregate.total_words)}</b>
          <span>累计简评字数</span>
        </div>
      </div>

      {/* Cohort summary */}
      {aggregate.cohort_summary && (
        <div className="report-summary mb-4">{aggregate.cohort_summary}</div>
      )}

      {/* Observations */}
      {aggregate.observations?.length > 0 && (
        <>
          <h2 className="h5 report-section-header">数据观察</h2>
          <div className="report-card mb-4">
            <ul className="report-observations">
              {aggregate.observations.map((o, i) => (
                <li key={i} className="report-observation">
                  <span className="report-obs-title">{o.title}</span>
                  <span className="report-obs-text">{o.text}</span>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {/* Topic axes */}
      <h2 className="h5 report-section-header">兴趣画像 · 研究主题轴</h2>
      <p className="text-body-secondary small">
        按论文标题/关键词/摘要命中统计（一条可命中多个主题）。这张表回答"这群人在读什么"。
      </p>
      <div className="report-card mb-4">
        <TopicBars axes={aggregate.topic_axes} />
      </div>

      {/* Common papers */}
      {aggregate.common_papers?.length > 0 && (
        <>
          <h2 className="h5 report-section-header">共同阅读 · 被多人分享的论文</h2>
          <p className="text-body-secondary small">
            被多位分享者先后读过的同一篇论文。
          </p>
          <div className="report-card mb-4">
            <ul className="report-common-list">
              {aggregate.common_papers.map((cp: CommonPaper) => (
                <li key={cp.paper_id} className="report-common">
                  <div className="report-paper-title">
                    <Link
                      to={`/group/${groupName}/review/${cp.review_id}`}
                      className="report-paper-link"
                    >
                      {cp.title}
                    </Link>
                    <span className="text-body-secondary small ms-1">
                      {cp.journal}
                      {cp.year ? ` (${cp.year})` : ""} · {cp.reader_count} 人读过
                    </span>
                  </div>
                  <div className="report-common-readers">
                    {cp.readers.map((r) => (
                      <Link
                        key={r.user_id}
                        to={`/group/${groupName}/user/${r.user_id}`}
                        className="report-topic-sm"
                      >
                        {r.name}
                      </Link>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}

      {/* Top journals */}
      <h2 className="h5 report-section-header">常读期刊</h2>
      <div className="report-card mb-4">
        <div className="d-flex flex-wrap gap-2">
          {Object.entries(aggregate.top_journals).map(([name, count]) => (
            <Link
              key={name}
              to={`/group/${groupName}/journal/${encodeURIComponent(name)}`}
              className="badge report-journal-badge"
            >
              {name} <span className="report-badge-count">{count}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Member tiers */}
      <div className="report-card mb-4">
        <div className="d-flex flex-wrap gap-3">
          {Object.entries(aggregate.member_tiers).map(([tier, count]) => (
            <span key={tier} className="report-metric-sm">
              <span className={`report-tier ${TIER_CLASS[tier] ?? ""}`}>{tier}</span>{" "}
              <b>{count}</b> 人
            </span>
          ))}
        </div>
      </div>

      {/* Members grid */}
      <h2 className="h5 report-section-header">历年分享者画像</h2>
      <p className="text-body-secondary small">
        点击分享者姓名，查看该分享者的完整评价画像。
      </p>
      <div className="report-grid">
        {members.map((m) => (
          <button
            key={m.user_id}
            type="button"
            className="report-member-btn"
            onClick={() => setSelected(m)}
          >
            <div className="d-flex align-items-center gap-2">
              <span className="report-member-name">{m.name}</span>
              <span className={`report-tier ${TIER_CLASS[m.reader_type] ?? ""}`}>
                {m.reader_type}
              </span>
            </div>
            <div className="report-member-meta">
              {m.review_count} 条 · {m.word_per_review} 字/条
              <span className="ms-1">
                <Link
                  to={`/group/${groupName}/user/${m.user_id}`}
                  onClick={(e) => e.stopPropagation()}
                >
                  分享
                </Link>
              </span>
            </div>
            {m.top_topics.length > 0 && (
              <div className="report-member-topics">
                {m.top_topics.slice(0, 2).map((t) => (
                  <span key={t} className="report-topic-sm">
                    {t}
                  </span>
                ))}
              </div>
            )}
          </button>
        ))}
      </div>

      <MemberProfileModal
        profile={selected}
        groupName={groupName!}
        onClose={() => setSelected(null)}
      />
    </section>
  );
}

export default MemberReportPage;
