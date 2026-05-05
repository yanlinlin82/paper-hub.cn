import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar({ groupName }) {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [appearanceDropdownOpen, setAppearanceDropdownOpen] = useState(false);
  const userDropdownRef = useRef(null);
  const appearanceDropdownRef = useRef(null);

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
        appearanceDropdownOpen &&
        appearanceDropdownRef.current &&
        !appearanceDropdownRef.current.contains(e.target)
      ) {
        setAppearanceDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [userDropdownOpen, appearanceDropdownOpen]);

  // Load dark mode preference
  useEffect(() => {
    const savedDarkMode = localStorage.getItem("darkMode") === "true";
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.setAttribute("data-bs-theme", "dark");
    }
  }, []);

  const toggleDarkMode = () => {
    const newVal = !darkMode;
    setDarkMode(newVal);
    localStorage.setItem("darkMode", newVal);
    document.documentElement.setAttribute(
      "data-bs-theme",
      newVal ? "dark" : "light",
    );
  };

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

  return (
    <nav className="navbar">
      <div className="container-xl d-flex align-items-center gap-3">
        {/* Brand */}
        <Link className="navbar-brand flex-shrink-0" to={`/group/${groupName}`}>
          <img
            src="/static/images/banner-b.png"
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

        {/* Right section */}
        <ul className="navbar-nav flex-shrink-0">
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
          <li
            ref={appearanceDropdownRef}
            className={`nav-item dropdown${appearanceDropdownOpen ? " show" : ""}`}
          >
            <a
              className="nav-link dropdown-toggle"
              href="#"
              role="button"
              onClick={(e) => {
                e.preventDefault();
                setAppearanceDropdownOpen(!appearanceDropdownOpen);
              }}
              aria-expanded={appearanceDropdownOpen}
            >
              主题
            </a>
            <ul
              className={`dropdown-menu dropdown-menu-end${appearanceDropdownOpen ? " show" : ""}`}
            >
              <li className="p-3">
                <div className="form-check form-switch">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    role="switch"
                    id="toggleTheme"
                    checked={darkMode}
                    onChange={toggleDarkMode}
                  />
                  <label className="form-check-label" htmlFor="toggleTheme">
                    深色模式
                  </label>
                </div>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
