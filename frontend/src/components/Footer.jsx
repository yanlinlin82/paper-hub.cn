import React from "react";

function Footer() {
  return (
    <footer
      className="text-center py-3 bg-body-tertiary border-top text-body-secondary"
      style={{ fontSize: "0.88rem" }}
    >
      <div className="py-1">
        <a
          className="text-reset"
          href="https://yanlinlin.cn/"
          target="_blank"
          rel="noreferrer"
        >
          &copy; 2022 - 2024
        </a>{" "}
        |{" "}
        <a
          className="text-reset"
          href="http://beian.miit.gov.cn/"
          target="_blank"
          rel="noreferrer"
        >
          京ICP备18031542号-9
        </a>{" "}
        |{" "}
        <a
          className="text-reset"
          href="https://github.com/yanlinlin82/paper-hub.cn/"
          target="_blank"
          rel="noreferrer"
        >
          GitHub
        </a>
      </div>
      <div className="py-1">
        基于{" "}
        <a
          className="text-reset"
          href="https://www.djangoproject.com/"
          target="_blank"
          rel="noreferrer"
        >
          Django
        </a>{" "}
        和{" "}
        <a
          className="text-reset"
          href="https://getbootstrap.com/"
          target="_blank"
          rel="noreferrer"
        >
          Bootstrap
        </a>{" "}
        和{" "}
        <a
          className="text-reset"
          href="https://react.dev/"
          target="_blank"
          rel="noreferrer"
        >
          React
        </a>{" "}
        开发
      </div>
    </footer>
  );
}

export default Footer;
