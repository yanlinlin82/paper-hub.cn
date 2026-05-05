import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar({ groupName }) {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [fullWidth, setFullWidth] = useState(false);
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

  useEffect(() => {
    const savedFullWidth = localStorage.getItem("fullWidth") === "true";
    const savedDarkMode = localStorage.getItem("darkMode") === "true";
    setFullWidth(savedFullWidth);
    setDarkMode(savedDarkMode);
    if (savedDarkMode) {
      document.documentElement.setAttribute("data-bs-theme", "dark");
    }
    if (savedFullWidth) {
      document
        .getElementById("mainContainer")
        ?.classList.remove("container-xl");
      document
        .getElementById("mainContainer")
        ?.classList.add("container-fluid");
    }
  }, []);

  const toggleFullWidth = () => {
    const newVal = !fullWidth;
    setFullWidth(newVal);
    localStorage.setItem("fullWidth", newVal);
    const container = document.getElementById("mainContainer");
    if (container) {
      container.classList.toggle("container-xl");
      container.classList.toggle("container-fluid");
    }
  };

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
    <nav className="navbar navbar-expand bg-body-tertiary border-bottom border-body">
      <div className="container-xl">
        <div style={{ minWidth: "200px" }}>
          <Link className="navbar-brand" to={`/group/${groupName}`}>
            <img
              className="img-fluid"
              src="/static/images/banner-b.png"
              width="150"
              height="40"
              alt="Paper-Hub"
            />
          </Link>
        </div>
        <div className="row" style={{ width: "100%" }}>
          <div className="col-12 col-lg-7">
            <form className="flex-fill" onSubmit={handleSearch}>
              <div
                className="input-group text-start"
                style={{ minWidth: "250px", maxWidth: "500px" }}
              >
                <input
                  id="q"
                  name="q"
                  className="form-control border-secondary-subtle"
                  type="search"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onFocus={() => setShowHint(true)}
                  onBlur={() => setTimeout(() => setShowHint(false), 200)}
                  placeholder="搜索文献"
                  aria-label="Search"
                />
                <button
                  className="btn btn-outline border-secondary-subtle text-nowrap"
                  type="submit"
                >
                  搜索
                </button>
                {showHint && (
                  <div
                    className="bg-light-subtle border border-warning p-3 text-danger"
                    style={{
                      position: "absolute",
                      zIndex: 1000,
                      top: "100%",
                      left: 0,
                      width: "100%",
                      borderRadius: "5px",
                    }}
                  >
                    <p>
                      <small>
                        注意：本站仅支持搜索站内已收录的文献
                        {user ? "，或根据ID获取单篇文献信息" : ""}
                        ，如需搜索更大范围的其他文献，请移步使用{" "}
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
                      </small>
                    </p>
                  </div>
                )}
              </div>
            </form>
          </div>
          <div className="col-12 col-lg-5">
            <ul className="navbar-nav nav justify-content-end ms-3">
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
                        <button
                          className="dropdown-item"
                          onClick={handleLogout}
                        >
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
                  外观
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
                        id="toggleContainer"
                        checked={fullWidth}
                        onChange={toggleFullWidth}
                      />
                      <label
                        className="form-check-label"
                        htmlFor="toggleContainer"
                      >
                        全宽显示
                      </label>
                    </div>
                  </li>
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
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
