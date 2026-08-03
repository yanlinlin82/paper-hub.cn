import React, { useState } from "react";
import { useParams } from "react-router";
import Offcanvas from "react-bootstrap/Offcanvas";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import LoginModal from "./LoginModal";
import ScrollToTop from "./ScrollToTop";
import Footer from "./Footer";

interface LayoutProps {
  children: React.ReactNode;
}

function Layout({ children }: LayoutProps) {
  const { groupName } = useParams<{ groupName?: string }>();
  const [showLogin, setShowLogin] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar
        groupName={groupName}
        onShowLogin={() => setShowLogin(true)}
        onToggleSidebar={() => setShowSidebar(true)}
      />

      <div className="flex-fill">
        <div className="container-xl py-4">
          <div className="row g-4">
            {/* Desktop sidebar */}
            <aside className="d-none d-lg-block col-lg-3 col-xxl-2">
              <div className="sidebar-sticky">
                <Sidebar groupName={groupName} />
              </div>
            </aside>

            {/* Main content */}
            <main className="col-lg-9 col-xxl-10">
              <article className="fade-in" style={{ minHeight: "60vh" }}>
                {children}
              </article>
            </main>
          </div>

          {/* Footer — full container width, below the flex row */}
          <Footer />
        </div>
      </div>

      {/* Mobile sidebar drawer */}
      <Offcanvas
        show={showSidebar}
        onHide={() => setShowSidebar(false)}
        placement="start"
      >
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>导航</Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body>
          <Sidebar groupName={groupName} />
        </Offcanvas.Body>
      </Offcanvas>

      <LoginModal show={showLogin} onClose={() => setShowLogin(false)} />
      <ScrollToTop />
    </div>
  );
}

export default Layout;
