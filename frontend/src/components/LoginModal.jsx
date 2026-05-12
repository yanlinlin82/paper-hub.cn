import React, { useState, useEffect } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import { useAuth } from "../context/AuthContext";

function LoginModal({ show, onClose }) {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (show) {
      setUsername("");
      setPassword("");
      setError("");
      setSubmitting(false);
    }
  }, [show]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const result = await login(username, password);
      if (result.success) {
        onClose();
      } else {
        setError(result.error || "登录失败");
      }
    } catch (err) {
      setError(err.message || "登录失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>登录</Modal.Title>
      </Modal.Header>
      <form onSubmit={handleSubmit}>
        <Modal.Body>
          {error && <div className="alert alert-danger py-2 mb-3">{error}</div>}
          <div className="mb-3">
            <label htmlFor="loginUsername" className="form-label">
              用户名
            </label>
            <input
              type="text"
              className="form-control"
              id="loginUsername"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoFocus
            />
          </div>
          <div className="mb-3">
            <label htmlFor="loginPassword" className="form-label">
              密码
            </label>
            <input
              type="password"
              className="form-control"
              id="loginPassword"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onClose}>
            取消
          </Button>
          <Button variant="primary" type="submit" disabled={submitting}>
            {submitting ? "登录中..." : "登录"}
          </Button>
        </Modal.Footer>
      </form>
    </Modal>
  );
}

export default LoginModal;
