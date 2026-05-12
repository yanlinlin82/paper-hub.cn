import React, { useState } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";

function CheckInModal({ groupName, onClose }) {
  const { user } = useAuth();

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

  const handleQuery = async () => {
    if (!identifier.trim()) return;
    setQuerying(true);
    try {
      const data = await api.post("/query-paper-info", {
        identifier: identifier.trim(),
      });

      if (data.paper) {
        setTitle(data.paper.title || "");
        setJournal(data.paper.journal || "");
        setPubDate(data.paper.pub_date || "");
        setAuthors(data.paper.authors || "");
        setAffiliations(data.paper.affiliations || "");
        setAbstract(data.paper.abstract || "");
        setKeywords(data.paper.keywords || "");
        setUrls(data.paper.urls || "");
        setDoi(data.paper.doi || "");
        setPmid(data.paper.pmid || "");
        setArxivId(data.paper.arxiv_id || "");
        setPmcid(data.paper.pmcid || "");
        setCnkiId(data.paper.cnki_id || "");
        setLanguage(data.paper.language || "eng");
        setMessage(data.paper.title || "");
        setShowManualInput(true);
      } else {
        setMessage("未找到该文献信息，请手动输入。");
        setShowManualInput(true);
      }
    } catch (err) {
      setMessage(err.message || "查询失败，请稍后重试。");
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
    if (value.trim().length >= 1) {
      try {
        const res = await api.get(
          `/search-users?q=${encodeURIComponent(value.trim())}`,
        );
        setAutocompleteItems(res.users || []);
        setShowAutocomplete(res.users?.length > 0);
      } catch {
        setShowAutocomplete(false);
      }
    } else {
      setShowAutocomplete(false);
    }
  };

  const selectAutocomplete = (item) => {
    setAdminUser(item);
    setShowAutocomplete(false);
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const payload = {
        group_name: groupName,
        paper: {
          title,
          journal,
          pub_date: pubDate,
          authors,
          affiliations,
          abstract,
          keywords,
          urls,
          doi,
          pmid,
          arxiv_id: arxivId,
          pmcid,
          cnki_id: cnkiId,
          language,
        },
        comment,
      };

      if (showAdminFields && adminUser) {
        payload.admin_user = adminUser;
      }
      if (showAdminFields && adminDate) {
        payload.admin_date = adminDate;
      }
      if (showAdminFields && adminTime) {
        payload.admin_time = adminTime;
      }

      const result = await api.post("/create-checkin", payload);
      if (result.success) {
        onClose();
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
    <Modal show={true} onHide={onClose} size="lg" backdrop="static" centered>
      <Modal.Header closeButton>
        <Modal.Title>文献分享打卡</Modal.Title>
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
            <label className="form-check-label" htmlFor="switchCheckInByAdmin">
              管理员补录
            </label>
          </div>
        )}
      </Modal.Header>
      <Modal.Body>
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

              {showDetail && (
                <div>
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

        {/* Admin fields */}
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
      </Modal.Body>

      <Modal.Footer>
        <Button variant="secondary" onClick={onClose}>
          取消
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={submitting}>
          {submitting ? "提交中..." : "提交"}
        </Button>
      </Modal.Footer>
    </Modal>
  );
}

function CheckInButton({ groupName }) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <div className="text-center my-3">
        <button
          className="btn btn-primary w-100 fw-semibold"
          onClick={() => setShowModal(true)}
        >
          + 分享打卡
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
