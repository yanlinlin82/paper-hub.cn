import { useEffect, useState } from "react";
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

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除该条配置吗？")) return;
    try {
      await api.deleteCustomCheckinInterval(id);
      await fetchIntervals();
    } catch (err) {
      setError((err as Error).message || "删除失败");
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
        <button className="btn btn-primary btn-sm" onClick={openCreateModal}>
          新增
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {intervals.length === 0 ? (
        <div className="my-5 text-center" style={{ minHeight: "200px" }}>
          暂无配置。点击"新增"按钮添加自定义打卡截止时间。
        </div>
      ) : (
        <table className="table table-bordered table-striped text-center mb-0">
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
                  <button
                    className="btn btn-outline-primary btn-sm me-2"
                    onClick={() => openEditModal(item)}
                  >
                    编辑
                  </button>
                  <button
                    className="btn btn-outline-danger btn-sm"
                    onClick={() => handleDelete(item.id)}
                  >
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {/* Modal for create/edit */}
      {showModal && (
        <div
          className="modal-backdrop-blur"
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0,0,0,0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1055,
          }}
          onClick={() => setShowModal(false)}
        >
          <div
            className="bg-body rounded shadow p-4"
            style={{ width: "420px", maxWidth: "90vw" }}
            onClick={(e) => e.stopPropagation()}
          >
            <h5 className="mb-3">{editingId ? "编辑配置" : "新增配置"}</h5>

            {message && (
              <div className="alert alert-danger py-2 small">{message}</div>
            )}

            <div className="mb-3">
              <label className="form-label">年份：</label>
              <input
                type="number"
                className="form-control"
                value={formYear}
                onChange={(e) => setFormYear(e.target.value)}
                placeholder="例如 2024"
              />
            </div>

            <div className="mb-3">
              <label className="form-label">月份：</label>
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
              <label className="form-label">截止时间：</label>
              <input
                type="datetime-local"
                className="form-control"
                value={formDeadline}
                onChange={(e) => setFormDeadline(e.target.value)}
              />
            </div>

            <div className="d-flex justify-content-end gap-2">
              <button
                className="btn btn-secondary"
                onClick={() => setShowModal(false)}
              >
                取消
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? "保存中..." : "保存"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default CustomCheckInIntervalConfig;
