import React from 'react';
import { useParams } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import LoginModal from './LoginModal';
import ScrollToTop from './ScrollToTop';
import Footer from './Footer';

function Layout({ children }) {
  const { groupName } = useParams();

  return (
    <div className="d-flex flex-column" style={{ width: '100vw', minHeight: '100vh' }}>
      <Navbar groupName={groupName} />
      <div id="mainContainer" className="flex-fill container-xl">
        <div className="d-flex flex-row" style={{ width: '100%', minHeight: 'calc(100vh - 56px)', minWidth: '600px' }}>
          <nav className="col-12" style={{ width: '200px', flex: '0 0 200px' }}>
            <div className="fixed-div">
              <Sidebar groupName={groupName} />
            </div>
          </nav>
          <div className="flex-fill text-start mt-3 ms-3 fixed-div">
            <div id="content" className="d-flex flex-column" style={{ height: '100%', overflowY: 'auto' }}>
              <a name="top"></a>
              <article className="flex-fill">
                {children}
              </article>
              <Footer />
            </div>
          </div>
        </div>
      </div>
      <LoginModal />
      <ScrollToTop />
    </div>
  );
}

export default Layout;
