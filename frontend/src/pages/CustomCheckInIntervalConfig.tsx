import { useEffect, useState } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import api from "../api/client";
import LoadingSpinner from "../components/LoadingSpinner";
import type { CustomCheckInInterval } from "../types";

function toLocalDatetimeString(dateStr: string): string {
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return "";
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function CustomCheckInIntervalConfig() {
  const [intervals, setIntervals] = useState<CustomCheckInInterval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formYear, setFormYear] = useState("");
  const [formMonth, setFormMonth] = useState("");
  const [formDeadline, setFormDeadline] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Delete confirmation state
  const [deleteTarget, setDeleteTarget] = useState<CustomCheckInInterval | null>(
    null,
  );
  const [deleting, setDeleting] = useState(false);

  const fetchIntervals = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.listCustomCheckinIntervals<{
        intervals: CustomCheckInInterval[];
      }>();
      setIntervals(result.intervals);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIntervals();
  }, []);

  const openCreateModal = () => {
    setEditingId(null);
    setFormYear("");
    setFormMonth("");
    setFormDeadline("");
    setMessage(null);
    setShowModal(true);
  };

  const openEditModal = (item: CustomCheckInInterval) => {
    setEditingId(item.id);
    setFormYear(String(item.year));
    setFormMonth(String(item.month));
    setFormDeadline(toLocalDatetimeString(item.deadline));
    setMessage(null);
    setShowModal(true);
  };

  const handleSave = async () => {
    if (!formYear || !formMonth || !formDeadline) {
      setMessage("请填写完整信息");
      return;
    }
    setSaving(true);
    setMessage(null);
    try {
      const payload = {
        year: parseInt(formYear),
        month: parseInt(formMonth),
        deadline: formDeadline,
      };
      if (editingId) {
        await api.updateCustomCheckinInterval(editingId, payload);
      } else {
        await api.createCustomCheckinInterval(payload);
      }
      setShowModal(false);
      await fetchIntervals();
    } catch (err) {
      setMessage((err as Error).message || "保存失败");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    setError(null);
    try {
      await api.deleteCustomCheckinInterval(deleteTarget.id);
      setDeleteTarget(null);
      await fetchIntervals();
    } catch (err) {
      setError((err as Error).message || "删除失败");
      setDeleteTarget(null);
    } finally {
      setDeleting(false);
    }
  };

  const formatDeadline = (isoStr: string) => {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return isoStr;
    return d.toLocaleString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) return <LoadingSpinner />;

  return (
    <section>
      <div className="d-flex align-items-center justify-content-between mb-3">
        <h4 className="mb-0">自定义打卡截止时间配置</h4>
        <Button variant="primary" size="sm" onClick={openCreateModal}>
          新增
        </Button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {intervals.length === 0 ? (
        <div className="card border-0 shadow-sm">
          <div className="card-body text-center text-body-secondary py-5">
            暂无配置。点击"新增"按钮添加自定义打卡截止时间。
          </div>
        </div>
      ) : (
        <div className="card border-0 shadow-sm">
          <div className="card-body p-0">
            <div className="table-responsive">
              <table className="table table-hover align-middle text-center mb-0">
                <thead>
                  <tr>
                    <th style={{ width: "20%" }}>年份</th>
                    <th style={{ width: "20%" }}>月份</th>
                    <th style={{ width: "40%" }}>截止时间</th>
                    <th style={{ width: "20%" }}>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {intervals.map((item) => (
                    <tr key={item.id}>
                      <td>{item.year}</td>
                      <td>{item.month}</td>
                      <td>{formatDeadline(item.deadline)}</td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          className="me-2"
                          onClick={() => openEditModal(item)}
                        >
                          编辑
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => setDeleteTarget(item)}
                        >
                          删除
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Modal for create/edit */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>{editingId ? "编辑配置" : "新增配置"}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {message && (
            <div className="alert alert-danger py-2 small">{message}</div>
          )}

          <div className="mb-3">
            <label className="form-label">年份</label>
            <input
              type="number"
              className="form-control"
              value={formYear}
              onChange={(e) => setFormYear(e.target.value)}
              placeholder="例如 2026"
            />
          </div>

          <div className="mb-3">
            <label className="form-label">月份</label>
            <input
              type="number"
              className="form-control"
              value={formMonth}
              onChange={(e) => setFormMonth(e.target.value)}
              placeholder="例如 6"
              min={1}
              max={12}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">截止时间</label>
            <input
              type="datetime-local"
              className="form-control"
              value={formDeadline}
              onChange={(e) => setFormDeadline(e.target.value)}
            />
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            取消
          </Button>
          <Button variant="primary" onClick={handleSave} disabled={saving}>
            {saving ? "保存中..." : "保存"}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Delete confirmation modal */}
      <Modal
        show={deleteTarget !== null}
        onHide={() => setDeleteTarget(null)}
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>删除配置</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p className="mb-0">
            确定要删除{" "}
            <strong>
              {deleteTarget?.year}年{deleteTarget?.month}月
            </strong>{" "}
            的打卡截止时间配置吗？
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
            取消
          </Button>
          <Button variant="danger" onClick={handleDelete} disabled={deleting}>
            {deleting ? "删除中..." : "确认删除"}
          </Button>
        </Modal.Footer>
      </Modal>
    </section>
  );
}

export default CustomCheckInIntervalConfig;
