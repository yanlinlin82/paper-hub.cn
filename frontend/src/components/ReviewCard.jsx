import React from "react";
import { Link } from "react-router-dom";
import PaperInfo from "./PaperInfo";

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
      <div>
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
    <div>
      {!expanded ? (
        <>
          {authorList.slice(0, 10).map((author, i) => (
            <span key={i}>{author}, </span>
          ))}
          ...
          <a
            href="#"
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
  const [showAbstract, setShowAbstract] = React.useState(false);

  return (
    <div
      id={`card_review_${review.id}`}
      className="review-card d-flex flex-row"
    >
      <div className="review-index p-2">{index}.</div>
      <div className="p-2 text-start flex-fill">
        {/* Review info */}
        <div className="d-flex flex-row">
          <div className="review-meta text-start flex-fill">
            <Link to={`/group/${groupName}/user/${review.creator_id}`}>
              {review.creator_name}
            </Link>
            ({formatDate(review.create_time)}):
          </div>
          {review.is_superuser && (
            <div className="admin-actions text-end align-self-start">
              <a
                className="btn btn-outline-primary btn-sm text-nowrap ms-2"
                href={`/admin/core/review/${review.id}/change/`}
                target="_blank"
                rel="noreferrer"
              >
                编辑分享
              </a>
              <a
                className="btn btn-outline-secondary btn-sm text-nowrap ms-2"
                href={`/admin/core/paper/${paper.id}/change/`}
                target="_blank"
                rel="noreferrer"
              >
                编辑文献
              </a>
            </div>
          )}
        </div>

        {/* Comment */}
        {review.comment && (
          <div
            className="review-comment"
            dangerouslySetInnerHTML={{ __html: review.comment }}
          />
        )}

        {/* Paper card */}
        <div className="paper-info-card">
          <PaperInfo paper={paper} groupName={groupName} />

          {/* Paper title */}
          {paper.title && (
            <div className="paper-title mt-2">
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
          <div className="author-list">
            <AuthorList authors={paper.authors} />
          </div>

          {/* Abstract */}
          {paper.abstract && (
            <div className="mt-2">
              <button
                className="abstract-toggle"
                onClick={(e) => {
                  e.preventDefault();
                  setShowAbstract(!showAbstract);
                }}
              >
                {showAbstract ? "▾ 收起摘要" : "▸ 展开摘要"}
              </button>
              {showAbstract && (
                <div
                  className="abstract-content"
                  dangerouslySetInnerHTML={{
                    __html: processXmlTags(paper.abstract),
                  }}
                />
              )}
            </div>
          )}

          {/* Keywords */}
          {paper.keywords && (
            <div className="keywords-label mt-2">
              <b>Keywords:</b>{" "}
              {paper.keywords
                .split("\n")
                .filter(Boolean)
                .map((kw, i, arr) => (
                  <span key={i} className="keyword-tag">
                    {kw}
                  </span>
                ))}
            </div>
          )}

          {/* URLs */}
          {paper.urls && (
            <div className="url-list">
              <b>Related Links:</b>
              <ul>
                {paper.urls
                  .split("\n")
                  .filter(Boolean)
                  .map((url, i) => (
                    <li key={i}>
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
      </div>
    </div>
  );
}

export default ReviewCard;
