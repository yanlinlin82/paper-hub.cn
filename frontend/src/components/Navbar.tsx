import React, { useRef, useState } from "react";
import { Link, useNavigate } from "react-router";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
import Form from "react-bootstrap/Form";
import Overlay from "react-bootstrap/Overlay";
import Popover from "react-bootstrap/Popover";
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

// Blur closes the hint, but a short delay lets a click on one of the links
// inside the popover complete before the popover unmounts.
const HINT_HIDE_DELAY_MS = 200;

function SiteNavbar({ groupName, onShowLogin, onToggleSidebar }: NavbarProps) {
  const { user, loading, logout } = useAuth();
  const { mode, setMode } = useTheme();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [showHint, setShowHint] = useState(false);
  const searchInput = useRef<HTMLInputElement>(null);

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

  const hideHintSoon = () => {
    window.setTimeout(() => setShowHint(false), HINT_HIDE_DELAY_MS);
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
    <Navbar
      sticky="top"
      bg="body-tertiary"
      className="border-bottom shadow-sm"
      expand="lg"
      onToggle={onToggleSidebar}
    >
      {/* justify-content-start overrides the space-between that Bootstrap
          applies to .navbar > .container-*: packing items from the start
          keeps the brand next to the drawer toggle, while ms-auto on the
          actions still pushes them to the right. */}
      <div className="container-xl d-flex flex-wrap justify-content-start align-items-center gap-2 gap-lg-3">
        {/* Mobile drawer toggle — shown by the framework below the lg
            breakpoint and hidden above it */}
        <Navbar.Toggle
          label="打开导航菜单"
          aria-controls="sidebar-drawer"
          className="flex-shrink-0"
        />

        {/* Brand */}
        <Navbar.Brand
          as={Link}
          to={`/group/${groupName}`}
          className="flex-shrink-0 me-0"
        >
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

        {/* Search — its own row below lg, middle column from lg up */}
        <Form
          className="navbar-search order-3 order-lg-2 mx-lg-3"
          onSubmit={handleSearch}
        >
          <div className="input-group">
            <input
              ref={searchInput}
              className="form-control"
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setShowHint(true)}
              onBlur={hideHintSoon}
              placeholder="搜索文献标题、作者、杂志..."
              aria-label="搜索"
            />
            <button className="btn btn-primary" type="submit">
              搜索
            </button>
          </div>
        </Form>

        <Overlay
          show={showHint}
          target={searchInput}
          placement="bottom-start"
          rootClose
          rootCloseEvent="mousedown"
          onHide={() => setShowHint(false)}
        >
          <Popover id="search-hint" style={{ maxWidth: "30rem" }}>
            <Popover.Body>
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
            </Popover.Body>
          </Popover>
        </Overlay>

        {/* Right-side actions.  They stay visible and horizontal at every
            width, so this block supplies the navbar-expand context itself:
            Bootstrap then keeps the nav row-directional and lifts its menus
            out of the flow, which is what a full navbar would do at all
            breakpoints. */}
        <div className="navbar-expand ms-auto order-2 order-lg-3">
          <Nav className="align-items-center gap-1 gap-lg-2">
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
                <NavDropdown id="account-menu" title={user.username} align="end">
                  <NavDropdown.Item as="button" onClick={handleLogout}>
                    退出登录
                  </NavDropdown.Item>
                </NavDropdown>
              </>
            ) : (
              <Nav.Item>
                <Nav.Link as="button" onClick={onShowLogin}>
                  登录
                </Nav.Link>
              </Nav.Item>
            )}

            {/* Theme toggle dropdown */}
            <NavDropdown id="theme-menu" title="主题" align="end">
              {themeOptions.map((opt) => (
                <NavDropdown.Item
                  key={opt.key}
                  as="button"
                  className="d-flex align-items-center gap-2"
                  onClick={() => setMode(opt.key)}
                >
                  <span>{opt.icon}</span>
                  <span>{opt.label}</span>
                  {mode === opt.key && (
                    <span className="ms-auto text-primary">✓</span>
                  )}
                </NavDropdown.Item>
              ))}
            </NavDropdown>
          </Nav>
        </div>
      </div>
    </Navbar>
  );
}

export default SiteNavbar;
