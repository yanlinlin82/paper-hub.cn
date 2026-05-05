import React, { useState, useEffect } from "react";

function ScrollToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setVisible(window.scrollY > 300);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (!visible) return null;

  return (
    <button
      className="btn btn-light border shadow-sm rounded-circle position-fixed"
      onClick={scrollToTop}
      aria-label="返回顶部"
      style={{
        bottom: "24px",
        right: "24px",
        zIndex: 999,
        width: "38px",
        height: "38px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        opacity: 0.85,
      }}
    >
      ↑
    </button>
  );
}

export default ScrollToTop;
