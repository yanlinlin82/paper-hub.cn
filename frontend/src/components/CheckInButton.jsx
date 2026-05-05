import React, { useState, useRef, useEffect, useCallback } from "react";
import { Modal } from "bootstrap";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";

function CheckInModal({ groupName, onClose }) {
  const { user } = useAuth();
  const modalRef = useRef(null);
  const bsModalRef = useRef(null);

  // Paper fields
  const [identifier, setIdentifier] = useState("");
  const [querying, setQuerying] = useState(false);
  const [showManualInput, setShowManualInput] = useState(false);
  const [showDetail, setShowDetail] = useState(false);
  const [showAdminFields, setShowAdminFields] = useState(false);
  const [message, setMessage] = useState(
    '请在上方输入文献ID，通过点击"提取文献信息"按钮，来自动获取文献信息。或者也可以点击右方的"手动输入"按钮，手动输入文献信息。',
  );

  // Form fields
  const [title, setTitle] = useState("");
  const [journal, setJournal] = useState("");
  const [pubDate, setPubDate] = useState("");
  const [authors, setAuthors] = useState("");
  const [affiliations, setAffiliations] = useState("");
  const [abstract, setAbstract] = useState("");
  const [keywords, setKeywords] = useState("");
  const [urls, setUrls] = useState("");
  const [doi, setDoi] = useState("");
  const [pmid, setPmid] = useState("");
  const [arxivId, setArxivId] = useState("");
  const [pmcid, setPmcid] = useState("");
  const [cnkiId, setCnkiId] = useState("");
  const [language, setLanguage] = useState("eng");
  const [comment, setComment] = useState("");
  const [adminUser, setAdminUser] = useState("");
  const [adminDate, setAdminDate] = useState("");
  const [adminTime, setAdminTime] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [autocompleteItems, setAutocompleteItems] = useState([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);

  useEffect(() => {
    if (modalRef.current && !bsModalRef.current) {
      bsModalRef.current = new Modal(modalRef.current);
      bsModalRef.current.show();
    }
  }, []);

  const closeModal = useCallback(() => {
    if (bsModalRef.current) {
      bsModalRef.current.hide();
      // Clean up modal backdrop
      const backdrops = document.querySelectorAll(".modal-backdrop");
      backdrops.forEach((b) => b.remove());
      document.body.classList.remove("modal-open");
      document.body.style.removeProperty("overflow");
      document.body.style.removeProperty("padding-right");
    }
    if (onClose) onClose();
  }, [onClose]);

  const handleQuery = async () => {
    if (!identifier.trim()) return;
    setQuerying(true);
    try {
      const data = await api.post("/query-paper-info", {
        identifier: identifier.trim(),
      });
      if (!data.success) {
        setMessage("查询失败: " + (data.error || "未知错误"));
        return;
      }
      const r = data.results;
      if (r.title) setTitle(r.title);
      if (r.journal) setJournal(r.journal);
      if (r.pub_date) setPubDate(r.pub_date);
      if (r.authors)
        setAuthors(Array.isArray(r.authors) ? r.authors.join("\n") : r.authors);
      if (r.affiliations)
        setAffiliations(
          Array.isArray(r.affiliations)
            ? r.affiliations.join("\n")
            : r.affiliations,
        );
      if (r.abstract) setAbstract(r.abstract);
      if (r.keywords)
        setKeywords(
          Array.isArray(r.keywords) ? r.keywords.join("\n") : r.keywords,
        );
      if (r.urls) setUrls(Array.isArray(r.urls) ? r.urls.join("\n") : r.urls);
      if (r.doi) setDoi(r.doi);
      if (r.pmid) setPmid(r.pmid);
      if (r.arxiv_id) setArxivId(r.arxiv_id);
      if (r.pmcid) setPmcid(r.pmcid);
      if (r.cnki_id) setCnkiId(r.cnki_id);
      if (r.language) setLanguage(r.language);
      setMessage("");
    } catch (err) {
      setMessage("查询失败: " + err.message);
    } finally {
      setQuerying(false);
    }
  };

  const handleIdentifierKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleQuery();
    }
  };

  const handleAdminUserChange = async (e) => {
    const value = e.target.value;
    setAdminUser(value);
    if (value.length < 1) {
      setShowAutocomplete(false);
      return;
    }
    try {
      const res = await api.get(
        `/username-autocomplete?term=${encodeURIComponent(value)}`,
      );
      if (Array.isArray(res)) {
        setAutocompleteItems(res.map((item) => item.value || item));
        setShowAutocomplete(true);
      }
    } catch {
      // ignore
    }
  };

  const selectAutocomplete = (item) => {
    setAdminUser(item);
    setShowAutocomplete(false);
  };

  const handleSubmit = async () => {
    if (!title.trim() || !journal.trim() || !pubDate.trim()) {
      setMessage("请至少填写标题、杂志和发表日期。");
      return;
    }
    setSubmitting(true);
    setMessage("");
    try {
      const payload = {
        group_name: groupName,
        paper: {
          title: title.trim(),
          journal: journal.trim(),
          pub_date: pubDate.trim(),
          authors: authors.trim(),
          affiliations: affiliations.trim(),
          abstract: abstract.trim(),
          keywords: keywords.trim(),
          urls: urls.trim(),
          doi: doi.trim(),
          pmid: pmid.trim(),
          arxiv_id: arxivId.trim(),
          pmcid: pmcid.trim(),
          cnki_id: cnkiId.trim(),
          language: language.trim() || "eng",
        },
        comment: comment.trim(),
      };
      if (showAdminFields && adminUser) {
        payload.username = adminUser.trim();
      }
      if (showAdminFields && adminDate) {
        payload.check_in_date = adminDate;
        if (adminTime) payload.check_in_time = adminTime;
      }
      const result = await api.post("/check-in", payload);
      if (result.success) {
        closeModal();
      } else {
        setMessage(result.error || "提交失败");
      }
    } catch (err) {
      setMessage(err.message || "提交失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      ref={modalRef}
      className="modal fade"
      id="checkInModal"
      data-bs-backdrop="static"
      tabIndex="-1"
      aria-labelledby="checkInModalLabel"
      aria-hidden="true"
    >
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">文献分享打卡</h5>
            {user?.is_superuser && <div className="flex-fill"></div>}
            {user?.is_superuser && (
              <div className="me-3 form-check form-switch">
                <input
                  className="form-check-input"
                  type="checkbox"
                  id="switchCheckInByAdmin"
                  checked={showAdminFields}
                  onChange={(e) => setShowAdminFields(e.target.checked)}
                />
                <label
                  className="form-check-label"
                  htmlFor="switchCheckInByAdmin"
                >
                  管理员补录
                </label>
              </div>
            )}
            <button
              type="button"
              className="btn-close"
              aria-label="Close"
              onClick={closeModal}
            ></button>
          </div>
          <div className="modal-body">
            {/* Identifier input */}
            <div className="row g-3 align-items-center mb-3">
              <div className="col-2"></div>
              <div className="col-2">
                <label className="form-label">文献ID：</label>
              </div>
              <div className="col-6">
                <div className="input-group">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="DOI/PMID/PMCID/arXivID"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    onKeyDown={handleIdentifierKeyDown}
                  />
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleQuery}
                    disabled={querying || !identifier.trim()}
                  >
                    {querying ? "查询中..." : "提取文献信息"}
                  </button>
                </div>
              </div>
              <div className="col-2"></div>
            </div>

            {/* Message / Paper info */}
            <div className="border p-3">
              <div className="row g-3 align-items-center mb-3">
                <div className="col-10 pt-3">
                  {message && <div className="text-danger">{message}</div>}
                  {title && (
                    <div className="text-start">
                      {journal && (
                        <div>
                          <i>{journal}</i>, {pubDate}.
                        </div>
                      )}
                      <div>
                        <b>{title}</b>
                      </div>
                    </div>
                  )}
                </div>
                <div className="col-2 text-end">
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => setShowManualInput(!showManualInput)}
                  >
                    {showManualInput ? "隐藏输入" : "手动输入"}
                  </button>
                </div>
              </div>

              {/* Manual input fields */}
              {showManualInput && (
                <div>
                  <hr />
                  {/* Title */}
                  <div className="row g-3 align-items-center mb-3">
                    <div className="col-2 text-end">
                      <label className="col-form-label">标题：</label>
                    </div>
                    <div className="col-10">
                      <input
                        type="text"
                        className="form-control"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  {/* Journal & PubDate */}
                  <div className="row g-3 align-items-center mb-3">
                    <div className="col-2 text-end">
                      <label className="col-form-label">杂志：</label>
                    </div>
                    <div className="col-3">
                      <input
                        type="text"
                        className="form-control"
                        value={journal}
                        onChange={(e) => setJournal(e.target.value)}
                        required
                      />
                    </div>
                    <div className="col-2 text-end">
                      <label className="col-form-label">发表日期：</label>
                    </div>
                    <div className="col-3">
                      <input
                        type="text"
                        className="form-control"
                        value={pubDate}
                        onChange={(e) => setPubDate(e.target.value)}
                        required
                      />
                    </div>
                    <div className="col-2 text-end">
                      <button
                        type="button"
                        className="btn btn-primary"
                        onClick={() => setShowDetail(!showDetail)}
                      >
                        {showDetail ? "收起更多" : "显示更多"}
                      </button>
                    </div>
                  </div>

                  {/* Detail fields */}
                  {showDetail && (
                    <div>
                      {/* Authors */}
                      <div className="row g-3 align-items-center mb-3">
                        <div className="col-2 text-end">
                          <label className="form-label">作者：</label>
                        </div>
                        <div className="col-10">
                          <textarea
                            className="form-control"
                            rows="2"
                            value={authors}
                            onChange={(e) => setAuthors(e.target.value)}
                          />
                        </div>
                      </div>
                      {/* Affiliations */}
                      <div className="row g-3 align-items-center mb-3">
                        <div className="col-2 text-end">
                          <label className="form-label">机构：</label>
                        </div>
                        <div className="col-10">
                          <textarea
                            className="form-control"
                            rows="2"
                            value={affiliations}
                            onChange={(e) => setAffiliations(e.target.value)}
                          />
                        </div>
                      </div>
                      {/* Abstract */}
                      <div className="row g-3 align-items-center mb-3">
                        <div className="col-2 text-end">
                          <label className="form-label">摘要：</label>
                        </div>
                        <div className="col-10">
                          <textarea
                            className="form-control"
                            rows="3"
                            value={abstract}
                            onChange={(e) => setAbstract(e.target.value)}
                          />
                        </div>
                      </div>
                      {/* Keywords */}
                      <div className="row g-3 align-items-center mb-3">
                        <div className="col-2 text-end">
                          <label className="form-label">关键词：</label>
                        </div>
                        <div className="col-10">
                          <textarea
                            className="form-control"
                            rows="2"
                            value={keywords}
                            onChange={(e) => setKeywords(e.target.value)}
                          />
                        </div>
                      </div>
                      {/* URLs */}
                      <div className="row g-3 align-items-center mb-3">
                        <div className="col-2 text-end">
                          <label className="form-label">链接：</label>
                        </div>
                        <div className="col-10">
                          <textarea
                            className="form-control"
                            rows="2"
                            value={urls}
                            onChange={(e) => setUrls(e.target.value)}
                          />
                        </div>
                      </div>
                      {/* DOI, PMID, arXiv ID */}
                      <div className="row g-3 align-items-center mb-3">
                        <div className="col-2 text-end">
                          <label className="form-label">DOI：</label>
                        </div>
                        <div className="col-2">
                          <input
                            type="text"
                            className="form-control"
                            value={doi}
                            onChange={(e) => setDoi(e.target.value)}
                          />
                        </div>
                        <div className="col-2 text-end">
                          <label className="form-label">PMID：</label>
                        </div>
                        <div className="col-2">
                          <input
                            type="text"
                            className="form-control"
                            value={pmid}
                            onChange={(e) => setPmid(e.target.value)}
                          />
                        </div>
                        <div className="col-2 text-end">
                          <label className="form-label">arXiv ID：</label>
                        </div>
                        <div className="col-2">
                          <input
                            type="text"
                            className="form-control"
                            value={arxivId}
                            onChange={(e) => setArxivId(e.target.value)}
                          />
                        </div>
                      </div>
                      {/* PMCID, CNKI, Language */}
                      <div className="row g-3 align-items-center mb-3">
                        <div className="col-2 text-end">
                          <label className="form-label">PMCID：</label>
                        </div>
                        <div className="col-2">
                          <input
                            type="text"
                            className="form-control"
                            value={pmcid}
                            onChange={(e) => setPmcid(e.target.value)}
                          />
                        </div>
                        <div className="col-2 text-end">
                          <label className="form-label">CNKI ID：</label>
                        </div>
                        <div className="col-2">
                          <input
                            type="text"
                            className="form-control"
                            value={cnkiId}
                            onChange={(e) => setCnkiId(e.target.value)}
                          />
                        </div>
                        <div className="col-2 text-end">
                          <label className="form-label">语言：</label>
                        </div>
                        <div className="col-2">
                          <input
                            type="text"
                            className="form-control"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Admin fields: creator & time */}
            {showAdminFields && (
              <div className="row g-3 align-items-center my-3">
                <div className="col-2 text-end">
                  <label className="col-form-label">打卡人：</label>
                </div>
                <div className="col-3" style={{ position: "relative" }}>
                  <input
                    className="form-control"
                    type="text"
                    value={adminUser}
                    onChange={handleAdminUserChange}
                    placeholder="用户名"
                  />
                  {showAutocomplete && autocompleteItems.length > 0 && (
                    <ul
                      style={{
                        position: "absolute",
                        zIndex: 2050,
                        background: "white",
                        border: "1px solid #ccc",
                        maxHeight: "200px",
                        overflowY: "auto",
                        width: "100%",
                        listStyle: "none",
                        padding: 0,
                        margin: 0,
                      }}
                    >
                      {autocompleteItems.map((item, i) => (
                        <li
                          key={i}
                          style={{
                            padding: "8px 12px",
                            cursor: "pointer",
                            borderBottom: "1px solid #eee",
                          }}
                          onMouseDown={() => selectAutocomplete(item)}
                          onMouseEnter={(e) =>
                            (e.target.style.background = "#f5f5f5")
                          }
                          onMouseLeave={(e) =>
                            (e.target.style.background = "white")
                          }
                        >
                          {item}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div className="col-2 text-end">
                  <label className="col-form-label">打卡时间：</label>
                </div>
                <div className="col-5">
                  <div className="input-group">
                    <input
                      type="date"
                      className="form-control"
                      value={adminDate}
                      onChange={(e) => setAdminDate(e.target.value)}
                    />
                    <input
                      type="time"
                      className="form-control"
                      value={adminTime}
                      onChange={(e) => setAdminTime(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Comment */}
            <div className="row g-3 align-items-center">
              <div className="form-group text-start">
                <label className="mt-3">评论：</label>
                <textarea
                  className="form-control my-2"
                  rows="6"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={closeModal}
            >
              取消
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={submitting}
            >
              {submitting ? "提交中..." : "提交"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function CheckInButton({ groupName }) {
  const [showModal, setShowModal] = useState(false);

  const handleClick = () => {
    setShowModal(true);
  };

  return (
    <>
      <div className="text-center my-3">
        <button
          className="btn btn-success btn-lg"
          onClick={handleClick}
          style={{ width: "160px" }}
        >
          分享打卡
        </button>
      </div>
      {showModal && (
        <CheckInModal
          groupName={groupName}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
}

export default CheckInButton;
