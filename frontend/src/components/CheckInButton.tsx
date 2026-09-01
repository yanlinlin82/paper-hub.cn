import React, { useRef, useState } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import api from "../api/client";

interface CheckInModalProps {
  groupName: string | undefined;
  onClose: () => void;
}

interface CheckInButtonProps {
  groupName: string | undefined;
}

function normalizeField(value: string | string[] | null | undefined): string {
  if (Array.isArray(value)) {
    return value.join("\n");
  }
  return value || "";
}

function CheckInModal({ groupName, onClose }: CheckInModalProps) {
  // Paper fields
  const [identifier, setIdentifier] = useState<string>("");
  const [querying, setQuerying] = useState<boolean>(false);
  const [showManualInput, setShowManualInput] = useState<boolean>(false);
  const [showDetail, setShowDetail] = useState<boolean>(false);
  const [message, setMessage] = useState<string>(
    '请在上方输入文献ID，通过点击"提取文献信息"按钮，来自动获取文献信息。或者也可以点击右方的"手动输入"按钮，手动输入文献信息。',
  );

  // Form fields
  const [title, setTitle] = useState<string>("");
  const [journal, setJournal] = useState<string>("");
  const [pubDate, setPubDate] = useState<string>("");
  const [authors, setAuthors] = useState<string>("");
  const [affiliations, setAffiliations] = useState<string>("");
  const [abstract, setAbstract] = useState<string>("");
  const [keywords, setKeywords] = useState<string>("");
  const [urls, setUrls] = useState<string>("");
  const [doi, setDoi] = useState<string>("");
  const [pmid, setPmid] = useState<string>("");
  const [arxivId, setArxivId] = useState<string>("");
  const [pmcid, setPmcid] = useState<string>("");
  const [cnkiId, setCnkiId] = useState<string>("");
  const [language, setLanguage] = useState<string>("eng");
  const [comment, setComment] = useState<string>("");
  const [checkinAt, setCheckinAt] = useState<string>(
    new Date().toLocaleDateString("sv-SE") +
      " " +
      new Date().toLocaleTimeString("sv-SE", {
        hour: "2-digit",
        minute: "2-digit",
      }),
  );
  const [adminUser, setAdminUser] = useState<string>("");
  const [submitting, setSubmitting] = useState<boolean>(false);
  // Guards against a double-click landing before the disabled state re-renders.
  const submittingRef = useRef<boolean>(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [autocompleteItems, setAutocompleteItems] = useState<any[]>([]);
  const [showAutocomplete, setShowAutocomplete] = useState<boolean>(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const handleQuery = async () => {
    if (!identifier.trim()) return;
    setQuerying(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const data: any = await api.post("/query-paper-info", {
        identifier: identifier.trim(),
      });

      if (data.paper) {
        setTitle(data.paper.title || "");
        setJournal(data.paper.journal || "");
        setPubDate(data.paper.pub_date || "");
        setAuthors(normalizeField(data.paper.authors));
        setAffiliations(normalizeField(data.paper.affiliations));
        setAbstract(data.paper.abstract || "");
        setKeywords(normalizeField(data.paper.keywords));
        setUrls(normalizeField(data.paper.urls));
        setDoi(data.paper.doi || "");
        setPmid(data.paper.pmid || "");
        setArxivId(data.paper.arxiv_id || "");
        setPmcid(data.paper.pmcid || "");
        setCnkiId(data.paper.cnki_id || "");
        setLanguage(data.paper.language || "eng");
        setMessage("");
        setShowManualInput(true);
      } else {
        setMessage("未找到该文献信息，请手动输入。");
        setShowManualInput(true);
      }
    } catch (err) {
      setMessage((err as Error).message || "查询失败，请稍后重试。");
    } finally {
      setQuerying(false);
    }
  };

  const handleIdentifierKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleQuery();
    }
  };

  const handleAdminUserChange = async (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const value = e.target.value;
    setAdminUser(value);
    setFieldErrors((prev) => ({ ...prev, adminUser: "" }));
    if (value.trim().length >= 1) {
      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const res: any = await api.get(
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

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const selectAutocomplete = (item: any) => {
    setAdminUser(item);
    setShowAutocomplete(false);
    setFieldErrors((prev) => ({ ...prev, adminUser: "" }));
  };

  const handleSubmit = async () => {
    if (submittingRef.current) return;
    if (!adminUser.trim()) {
      setFieldErrors({ adminUser: "请输入打卡人" });
      return;
    }
    setFieldErrors({});
    submittingRef.current = true;
    setSubmitting(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const payload: Record<string, any> = {
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

      if (checkinAt) {
        payload.checkin_at = checkinAt;
      }
      if (adminUser) {
        payload.admin_user = adminUser;
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result: any = await api.post("/check-in", payload);
      if (result.success) {
        onClose();
        window.location.reload();
      } else {
        setMessage(result.error || "提交失败");
      }
    } catch (err) {
      setMessage((err as Error).message || "提交失败");
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  };

  return (
    <Modal show={true} onHide={onClose} size="lg" backdrop="static" centered>
      <Modal.Header closeButton>
        <Modal.Title>文献分享打卡</Modal.Title>
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
              {message && (
                <div
                  className="text-danger"
                  style={{
                    maxHeight: "200px",
                    overflowY: "auto",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {message}
                </div>
              )}
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
                        rows={2}
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
                        rows={2}
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
                        rows={3}
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
                        rows={2}
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
                        rows={2}
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

        {/* Admin user + check-in time */}
        <div className="row g-3 align-items-center mt-3 mb-2">
          <div className="col-2 text-end">
            <label className="col-form-label">打卡人：</label>
          </div>
          <div className="col-3" style={{ position: "relative" }}>
            <input
              className={`form-control${fieldErrors.adminUser ? " is-invalid" : ""}`}
              type="text"
              value={adminUser}
              onChange={handleAdminUserChange}
              placeholder="用户名"
            />
            {fieldErrors.adminUser && (
              <div className="invalid-feedback d-block">
                {fieldErrors.adminUser}
              </div>
            )}
            {showAutocomplete && autocompleteItems.length > 0 && (
              <ul className="autocomplete-dropdown">
                {autocompleteItems.map((item: string, i: number) => (
                  <li key={i} onMouseDown={() => selectAutocomplete(item)}>
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
            <div className="d-flex gap-2">
              <input
                type="date"
                className="form-control"
                style={{ minWidth: 0, width: "140px", flex: "0 0 auto" }}
                value={checkinAt.slice(0, 10)}
                onChange={(e) =>
                  setCheckinAt(e.target.value + " " + checkinAt.slice(11, 16))
                }
              />
              <input
                type="time"
                className="form-control"
                style={{ minWidth: 0, width: "130px", flex: "0 0 auto" }}
                value={checkinAt.slice(11, 16)}
                onChange={(e) =>
                  setCheckinAt(checkinAt.slice(0, 10) + " " + e.target.value)
                }
              />
            </div>
          </div>
        </div>

        {/* Comment */}
        <div className="row g-3 align-items-center">
          <div className="form-group text-start">
            <label className="mt-3">评论：</label>
            <textarea
              className="form-control my-2"
              rows={6}
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

function CheckInButton({ groupName }: CheckInButtonProps) {
  const [showModal, setShowModal] = useState<boolean>(false);

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
