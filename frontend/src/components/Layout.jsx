import React, { useState } from "react";
import { useParams } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import LoginModal from "./LoginModal";
import ScrollToTop from "./ScrollToTop";
import Footer from "./Footer";

function Layout({ children }) {
  const { groupName } = useParams();
  const [showLogin, setShowLogin] = useState(false);

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar groupName={groupName} onShowLogin={() => setShowLogin(true)} />
      <div className="flex-fill">
        <div className="container-xl d-flex flex-column">
          <div className="d-flex flex-row align-items-start pt-4">
            {/* Sidebar */}
            <aside
              style={{ width: "200px", flex: "0 0 200px" }}
              className="pe-3"
            >
              <div className="sidebar-sticky">
                <Sidebar groupName={groupName} />
              </div>
            </aside>

            {/* Main content */}
            <main className="flex-fill pb-4" style={{ minWidth: 0 }}>
              <article className="fade-in" style={{ minHeight: "60vh" }}>
                {children}
              </article>
            </main>
          </div>

          {/* Footer — full container width, below the flex row */}
          <Footer />
        </div>
      </div>
      <LoginModal show={showLogin} onClose={() => setShowLogin(false)} />
      <ScrollToTop />
    </div>
  );
}

export default Layout;
