import React from "react";
import { useParams } from "react-router-dom";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import LoginModal from "./LoginModal";
import ScrollToTop from "./ScrollToTop";
import Footer from "./Footer";

function Layout({ children }) {
  const { groupName } = useParams();

  return (
    <div className="d-flex flex-column min-vh-100">
      <Navbar groupName={groupName} />
      <div id="mainContainer" className="flex-fill">
        <div className="container-xl d-flex flex-row layout-body">
          {/* Sidebar — sticky on scroll */}
          <aside className="layout-sidebar">
            <div className="sidebar-sticky">
              <Sidebar groupName={groupName} />
            </div>
          </aside>

          {/* Main content — single scroll with page */}
          <main className="layout-content">
            <article className="fade-in">{children}</article>
            <Footer />
          </main>
        </div>
      </div>
      <LoginModal />
      <ScrollToTop />
    </div>
  );
}

export default Layout;
