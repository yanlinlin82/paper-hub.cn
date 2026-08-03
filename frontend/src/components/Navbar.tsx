import React, { useState } from "react";
import { Link, useNavigate } from "react-router";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
import Form from "react-bootstrap/Form";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { ThemeMode } from "../types";

interface NavbarProps {
  groupName: string | undefined;
  onShowLogin: () => void;
  onToggleSidebar: () => void;
}

interface ThemeOption {
  key: ThemeMode;
  label: string;
  icon: React.ReactNode;
}

function SiteNavbar({ groupName, onShowLogin, onToggleSidebar }: NavbarProps) {
  const { user, loading, logout } = useAuth();
  const { mode, setMode } = useTheme();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [showHint, setShowHint] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/group/${groupName}/all?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate(`/group/${groupName}`);
  };

  const themeOptions: ThemeOption[] = [
    {
      key: "light",
      label: "浅色",
      icon: (
        <svg viewBox="0 0 20 20" width="16" height="16" fill="currentColor">
          <circle cx="10" cy="10" r="4" />
          <path
            d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.42 1.42M13.65 13.65l1.42 1.42M4.93 15.07l1.42-1.42M13.65 6.35l1.42-1.42"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            fill="none"
          />
        </svg>
      ),
    },
    {
      key: "dark",
      label: "深色",
      icon: (
        <svg viewBox="0 0 20 20" width="16" height="16" fill="currentColor">
          <path d="M17.293 13.293A8 8 0 0 1 6.707 2.707a8.001 8.001 0 1 0 10.586 10.586Z" />
        </svg>
      ),
    },
    {
      key: "system",
      label: "跟随系统",
      icon: (
        <svg
          viewBox="0 0 20 20"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <rect x="1" y="2" width="18" height="12" rx="2" />
          <path d="M7 16l-1 3h8l-1-3" />
          <path d="M10 15v1" />
        </svg>
      ),
    },
  ];

  return (
    <Navbar sticky="top" bg="body-tertiary" className="border-bottom shadow-sm">
      <div className="container-xl d-flex flex-wrap align-items-center gap-2 gap-lg-3">
        {/* Brand */}
        <Navbar.Brand as={Link} to={`/group/${groupName}`} className="flex-shrink-0 me-0">
          <img
            className="logo-light"
            src="/static/images/banner-b.png"
            width="150"
            height="40"
            alt="Paper-Hub"
          />
          <img
            className="logo-dark"
            src="/static/images/banner-w.png"
            width="150"
            height="40"
            alt="Paper-Hub"
          />
        </Navbar.Brand>

        {/* Mobile sidebar toggle */}
        <button
          className="navbar-toggler d-lg-none ms-auto"
          type="button"
          onClick={onToggleSidebar}
          aria-label="打开导航菜单"
        >
          <span className="navbar-toggler-icon" />
        </button>

        {/* Search */}
        <Form
          className="flex-grow-1 order-3 order-lg-2 mx-lg-3 my-2 my-lg-0"
          onSubmit={handleSearch}
        >
          <div className="input-group" style={{ maxWidth: "480px" }}>
            <input
              className="form-control"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setShowHint(true)}
              onBlur={() => setTimeout(() => setShowHint(false), 200)}
              placeholder="搜索文献标题、作者、杂志..."
              aria-label="搜索"
            />
            <button className="btn btn-primary" type="submit">
              搜索
            </button>
            {showHint && (
              <div className="search-hint">
                <p className="mb-0">
                  注意：本站仅支持搜索站内已收录的文献
                  {user ? "，或根据ID获取单篇文献信息" : ""}
                  。如需搜索更大范围的其他文献，请移步使用{" "}
                  <a
                    href="https://pubmed.ncbi.nlm.nih.gov/"
                    target="_blank"
                    rel="noreferrer"
                    className="external-link"
                  >
                    PubMed
                  </a>
                  、
                  <a
                    href="https://scholar.google.com/"
                    target="_blank"
                    rel="noreferrer"
                    className="external-link"
                  >
                    Google Scholar
                  </a>{" "}
                  或{" "}
                  <a
                    href="https://arxiv.org/"
                    target="_blank"
                    rel="noreferrer"
                    className="external-link"
                  >
                    arXiv
                  </a>{" "}
                  等其他网站。
                </p>
              </div>
            )}
          </div>
        </Form>

        {/* Right-side actions */}
        <Nav className="order-2 order-lg-3 ms-auto flex-row align-items-center gap-1 gap-lg-2">
          {loading ? (
            <Nav.Item>
              <Nav.Link disabled>加载中...</Nav.Link>
            </Nav.Item>
          ) : user ? (
            <>
              <Nav.Item>
                <Nav.Link as={Link} to={`/group/${groupName}`}>
                  社群
                </Nav.Link>
              </Nav.Item>
              {user.is_superuser && (
                <Nav.Item>
                  <Nav.Link href="/admin/">管理后台</Nav.Link>
                </Nav.Item>
              )}
              <NavDropdown title={user.username} align="end">
                <NavDropdown.Item as="button" onClick={handleLogout}>
                  退出登录
                </NavDropdown.Item>
              </NavDropdown>
            </>
          ) : (
            <Nav.Item>
              <Nav.Link onClick={onShowLogin}>登录</Nav.Link>
            </Nav.Item>
          )}

          {/* Theme toggle dropdown */}
          <NavDropdown title="主题" align="end">
            {themeOptions.map((opt) => (
              <NavDropdown.Item
                key={opt.key}
                as="button"
                className="d-flex align-items-center gap-2"
                onClick={() => setMode(opt.key)}
              >
                <span>{opt.icon}</span>
                <span>{opt.label}</span>
                {mode === opt.key && <span className="ms-auto text-primary">✓</span>}
              </NavDropdown.Item>
            ))}
          </NavDropdown>
        </Nav>
      </div>
    </Navbar>
  );
}

export default SiteNavbar;
