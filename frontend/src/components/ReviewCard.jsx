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
  const [showAbstract, setShowAbstract] = React.useState(false);

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
                <a
                  className="btn btn-outline-primary btn-sm"
                  href={`/admin/core/review/${review.id}/change/`}
                  target="_blank"
                  rel="noreferrer"
                >
                  编辑分享
                </a>
                <a
                  className="btn btn-outline-secondary btn-sm"
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
              className="my-2"
              style={{ fontSize: "0.92rem", lineHeight: 1.75 }}
              dangerouslySetInnerHTML={{ __html: review.comment }}
            />
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
        </div>
      </div>
    </div>
  );
}

export default ReviewCard;
