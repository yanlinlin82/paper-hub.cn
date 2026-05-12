import React, { useState } from "react";
import { Link } from "react-router-dom";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import PaperInfo from "./PaperInfo";
import api from "../api/client";

function formatDate(dateStr) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function processXmlTags(text) {
  if (!text) return "";
  return text
    .replace(/\n/g, "<br>")
    .replace(/\s+/g, " ")
    .replace(/<\/?jats:bold>/g, "<b>")
    .replace(/<\/?jats:italic>/g, "<i>")
    .replace(/<\/?jats:[^>]+>/g, "");
}

function AuthorList({ authors }) {
  if (!authors) return null;
  const authorList = authors.split("\n").filter(Boolean);
  if (authorList.length === 0) return null;
  const [expanded, setExpanded] = React.useState(false);

  if (authorList.length <= 10) {
    return (
      <div className="text-body-secondary" style={{ fontSize: "0.85rem" }}>
        {authorList.map((author, i) => (
          <span key={i}>
            {author}
            {i < authorList.length - 1 ? ", " : ""}
          </span>
        ))}
      </div>
    );
  }

  return (
    <div className="text-body-secondary" style={{ fontSize: "0.85rem" }}>
      {!expanded ? (
        <>
          {authorList.slice(0, 10).map((author, i) => (
            <span key={i}>{author}, </span>
          ))}
          ...
          <a
            href="#"
            className="ms-1"
            onClick={(e) => {
              e.preventDefault();
              setExpanded(true);
            }}
          >
            &gt;&gt;&gt;
          </a>
        </>
      ) : (
        <>
          {authorList.map((author, i) => (
            <span key={i}>
              {author}
              {i < authorList.length - 1 ? ", " : ""}
            </span>
          ))}
          <a
            href="#"
            className="ms-1"
            onClick={(e) => {
              e.preventDefault();
              setExpanded(false);
            }}
          >
            &lt;&lt;&lt;
          </a>
        </>
      )}
    </div>
  );
}

function ReviewCard({
  review,
  index,
  groupName,
  showReviewLink = true,
  isTrash = false,
}) {
  const paper = review.paper || {};
  const [showAbstract, setShowAbstract] = useState(false);
  const [editingComment, setEditingComment] = useState(false);
  const [editCommentText, setEditCommentText] = useState(review.comment || "");
  const [editingPaper, setEditingPaper] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  return (
    <div className="card mb-3">
      <div className="card-body d-flex">
        <div
          className="text-body-tertiary fw-semibold pe-2 text-center"
          style={{ minWidth: "2rem", fontSize: "0.85rem" }}
        >
          {index}.
        </div>
        <div className="flex-fill">
          {/* Review meta */}
          <div className="d-flex flex-row">
            <div
              className="text-body-tertiary flex-fill"
              style={{ fontSize: "0.85rem" }}
            >
              <Link
                to={`/group/${groupName}/user/${review.creator_id}`}
                className="fw-semibold"
              >
                {review.creator_name}
              </Link>
              ({formatDate(review.create_time)}):
            </div>
            {review.is_superuser && (
              <div className="d-flex gap-1 flex-shrink-0">
                <button
                  className="btn btn-outline-primary btn-sm"
                  onClick={() => {
                    setEditCommentText(review.comment || "");
                    setEditingComment(!editingComment);
                    setEditingPaper(false);
                    setError("");
                  }}
                >
                  编辑分享
                </button>
                {!isTrash && (
                  <>
                    <button
                      className="btn btn-outline-secondary btn-sm"
                      onClick={() => {
                        setEditingPaper(!editingPaper);
                        setEditingComment(false);
                        setError("");
                      }}
                    >
                      编辑文献
                    </button>
                    <button
                      className="btn btn-outline-danger btn-sm"
                      onClick={() => setConfirmDelete(true)}
                    >
                      删除文献
                    </button>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Comment */}
          {review.comment && !editingComment && (
            <div
              className="my-2"
              style={{ fontSize: "0.92rem", lineHeight: 1.75 }}
              dangerouslySetInnerHTML={{ __html: review.comment }}
            />
          )}

          {/* Inline comment editor */}
          {editingComment && (
            <div className="my-2">
              <textarea
                className="form-control form-control-sm"
                rows="3"
                value={editCommentText}
                onChange={(e) => setEditCommentText(e.target.value)}
              />
              {error && <div className="text-danger mt-1 small">{error}</div>}
              <div className="mt-1 d-flex gap-2">
                <button
                  className="btn btn-primary btn-sm"
                  disabled={saving}
                  onClick={async () => {
                    setSaving(true);
                    setError("");
                    try {
                      await api.editReview(review.id, editCommentText);
                      review.comment = editCommentText;
                      setEditingComment(false);
                    } catch (err) {
                      setError(err.message || "保存失败");
                    } finally {
                      setSaving(false);
                    }
                  }}
                >
                  {saving ? "保存中..." : "保存"}
                </button>
                <button
                  className="btn btn-outline-secondary btn-sm"
                  onClick={() => setEditingComment(false)}
                >
                  取消
                </button>
              </div>
            </div>
          )}

          {/* Paper card */}
          <div className="paper-info-card">
            <PaperInfo paper={paper} groupName={groupName} />

            {/* Paper title */}
            {paper.title && (
              <div
                className="fw-semibold mt-2"
                style={{ fontSize: "0.95rem", lineHeight: 1.5 }}
              >
                {showReviewLink ? (
                  <Link to={`/group/${groupName}/review/${review.id}`}>
                    <span
                      dangerouslySetInnerHTML={{
                        __html: processXmlTags(paper.title),
                      }}
                    />
                  </Link>
                ) : (
                  <span
                    dangerouslySetInnerHTML={{
                      __html: processXmlTags(paper.title),
                    }}
                  />
                )}
              </div>
            )}

            {/* Authors */}
            <AuthorList authors={paper.authors} />

            {/* Abstract */}
            {paper.abstract && (
              <div className="mt-2">
                <button
                  className="btn btn-sm btn-outline-primary py-0 px-1"
                  onClick={() => setShowAbstract(!showAbstract)}
                  style={{ fontSize: "0.82rem" }}
                >
                  {showAbstract ? "▾ 收起摘要" : "▸ 展开摘要"}
                </button>
                {showAbstract && (
                  <div
                    className="border rounded p-2 mt-1 text-body-secondary"
                    style={{ fontSize: "0.88rem", lineHeight: 1.7 }}
                    dangerouslySetInnerHTML={{
                      __html: processXmlTags(paper.abstract),
                    }}
                  />
                )}
              </div>
            )}

            {/* Keywords */}
            {paper.keywords && (
              <div className="mt-2" style={{ fontSize: "0.82rem" }}>
                <span className="fw-medium text-body-secondary">
                  Keywords:{" "}
                </span>
                {paper.keywords
                  .split("\n")
                  .filter(Boolean)
                  .map((kw, i) => (
                    <span
                      key={i}
                      className="badge bg-light text-primary fw-normal me-1"
                    >
                      {kw}
                    </span>
                  ))}
              </div>
            )}

            {/* URLs */}
            {paper.urls && (
              <div
                className="mt-2 pt-2 border-top"
                style={{ fontSize: "0.8rem" }}
              >
                <span className="fw-medium">Related Links:</span>
                <ul className="list-unstyled mb-0 mt-1">
                  {paper.urls
                    .split("\n")
                    .filter(Boolean)
                    .map((url, i) => (
                      <li key={i} className="text-truncate">
                        <a
                          href={url}
                          target="_blank"
                          rel="noreferrer"
                          className="external-link"
                        >
                          {url}
                        </a>
                      </li>
                    ))}
                </ul>
              </div>
            )}
          </div>

          {/* Inline paper editor */}
          {editingPaper && (
            <div className="mt-3 p-3 border rounded">
              <h6 className="mb-3">编辑文献信息</h6>
              <div className="mb-2">
                <label className="form-label small mb-1">标题</label>
                <input
                  className="form-control form-control-sm"
                  type="text"
                  defaultValue={paper.title}
                  id={`paper-title-${review.id}`}
                />
              </div>
              <div className="mb-2">
                <label className="form-label small mb-1">期刊</label>
                <input
                  className="form-control form-control-sm"
                  type="text"
                  defaultValue={paper.journal}
                  id={`paper-journal-${review.id}`}
                />
              </div>
              <div className="mb-2">
                <label className="form-label small mb-1">作者</label>
                <textarea
                  className="form-control form-control-sm"
                  rows="2"
                  defaultValue={paper.authors}
                  id={`paper-authors-${review.id}`}
                />
              </div>
              {error && <div className="text-danger mt-1 small">{error}</div>}
              <div className="d-flex gap-2 mt-2">
                <button
                  className="btn btn-primary btn-sm"
                  disabled={saving}
                  onClick={async () => {
                    setSaving(true);
                    setError("");
                    try {
                      const titleInput = document.getElementById(
                        `paper-title-${review.id}`,
                      );
                      const journalInput = document.getElementById(
                        `paper-journal-${review.id}`,
                      );
                      const authorsInput = document.getElementById(
                        `paper-authors-${review.id}`,
                      );
                      await api.editPaper(review.id, paper.id, {
                        paper: {
                          title: titleInput.value,
                          journal: journalInput.value,
                          authors: authorsInput.value,
                        },
                      });
                      paper.title = titleInput.value;
                      paper.journal = journalInput.value;
                      paper.authors = authorsInput.value;
                      setEditingPaper(false);
                    } catch (err) {
                      setError(err.message || "保存失败");
                    } finally {
                      setSaving(false);
                    }
                  }}
                >
                  {saving ? "保存中..." : "保存"}
                </button>
                <button
                  className="btn btn-outline-secondary btn-sm"
                  onClick={() => setEditingPaper(false)}
                >
                  取消
                </button>
              </div>
            </div>
          )}

          {/* Delete confirmation modal */}
          <Modal
            show={confirmDelete}
            onHide={() => {
              setConfirmDelete(false);
              setError("");
            }}
            centered
          >
            <Modal.Header closeButton>
              <Modal.Title>删除打卡记录</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <p>确认删除该文献的打卡记录？</p>
              <p className="small text-body-secondary mb-0">
                仅删除你的打卡记录，不影响其他用户的打卡。
              </p>
              {error && <div className="text-danger mt-2 small">{error}</div>}
            </Modal.Body>
            <Modal.Footer>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  setConfirmDelete(false);
                  setError("");
                }}
              >
                取消
              </Button>
              <Button
                variant="danger"
                size="sm"
                disabled={saving}
                onClick={async () => {
                  setSaving(true);
                  setError("");
                  try {
                    await api.removePaper(paper.id);
                    setConfirmDelete(false);
                    window.location.reload();
                  } catch (err) {
                    setError(err.message || "删除失败");
                  } finally {
                    setSaving(false);
                  }
                }}
              >
                {saving ? "删除中..." : "确认删除"}
              </Button>
            </Modal.Footer>
          </Modal>
        </div>
      </div>
    </div>
  );
}

export default ReviewCard;
