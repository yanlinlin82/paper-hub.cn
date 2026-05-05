import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

function Navbar({ groupName }) {
  const { user, loading, logout } = useAuth();
  const { mode, setMode } = useTheme();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [showHint, setShowHint] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [themeDropdownOpen, setThemeDropdownOpen] = useState(false);
  const userDropdownRef = useRef(null);
  const themeDropdownRef = useRef(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        userDropdownOpen &&
        userDropdownRef.current &&
        !userDropdownRef.current.contains(e.target)
      ) {
        setUserDropdownOpen(false);
      }
      if (
        themeDropdownOpen &&
        themeDropdownRef.current &&
        !themeDropdownRef.current.contains(e.target)
      ) {
        setThemeDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [userDropdownOpen, themeDropdownOpen]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/group/${groupName}/all?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate(`/group/${groupName}`);
  };

  const themeOptions = [
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
    <nav className="navbar">
      <div className="container-xl d-flex align-items-center gap-3">
        {/* Brand */}
        <Link className="navbar-brand flex-shrink-0" to={`/group/${groupName}`}>
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
        </Link>

        {/* Search */}
        <form className="flex-grow-1" onSubmit={handleSearch}>
          <div className="input-group" style={{ maxWidth: "480px" }}>
            <input
              className="form-control"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setShowHint(true)}
              onBlur={() => setTimeout(() => setShowHint(false), 200)}
              placeholder="搜索文献标题、作者、杂志..."
              aria-label="Search"
            />
            <button className="btn" type="submit">
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
        </form>

        {/* Right section — keep on one line */}
        <ul className="navbar-nav flex-shrink-0 navbar-right">
          {loading ? (
            <li className="nav-item">
              <span className="nav-link">加载中...</span>
            </li>
          ) : user ? (
            <>
              <li className="nav-item">
                <Link className="nav-link" to={`/group/${groupName}`}>
                  社群
                </Link>
              </li>
              {user.is_superuser && (
                <li className="nav-item">
                  <a className="nav-link" href="/admin/">
                    管理后台
                  </a>
                </li>
              )}
              <li
                ref={userDropdownRef}
                className={`nav-item dropdown${userDropdownOpen ? " show" : ""}`}
              >
                <a
                  className="nav-link dropdown-toggle"
                  href="#"
                  role="button"
                  onClick={(e) => {
                    e.preventDefault();
                    setUserDropdownOpen(!userDropdownOpen);
                  }}
                  aria-expanded={userDropdownOpen}
                >
                  {user.username}
                </a>
                <ul
                  className={`dropdown-menu dropdown-menu-end${userDropdownOpen ? " show" : ""}`}
                >
                  <li>
                    <button className="dropdown-item" onClick={handleLogout}>
                      退出登录
                    </button>
                  </li>
                </ul>
              </li>
            </>
          ) : (
            <li className="nav-item">
              <a
                className="nav-link"
                href="#"
                data-bs-toggle="modal"
                data-bs-target="#loginModal"
              >
                登录
              </a>
            </li>
          )}

          {/* Theme toggle dropdown */}
          <li
            ref={themeDropdownRef}
            className={`nav-item dropdown${themeDropdownOpen ? " show" : ""}`}
          >
            <a
              className="nav-link dropdown-toggle"
              href="#"
              role="button"
              onClick={(e) => {
                e.preventDefault();
                setThemeDropdownOpen(!themeDropdownOpen);
              }}
              aria-expanded={themeDropdownOpen}
            >
              主题
            </a>
            <ul
              className={`dropdown-menu dropdown-menu-end${themeDropdownOpen ? " show" : ""}`}
            >
              {themeOptions.map((opt) => (
                <li key={opt.key}>
                  <button
                    className={`dropdown-item d-flex align-items-center gap-2 ${mode === opt.key ? "active" : ""}`}
                    onClick={() => {
                      setMode(opt.key);
                      setThemeDropdownOpen(false);
                    }}
                  >
                    <span>{opt.icon}</span>
                    <span>{opt.label}</span>
                    {mode === opt.key && (
                      <span className="ms-auto text-primary">✓</span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
