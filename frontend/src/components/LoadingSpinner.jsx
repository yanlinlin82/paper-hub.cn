import React from "react";

function LoadingSpinner({ text = "加载中..." }) {
  return (
    <div
      className="d-flex flex-column align-items-center justify-content-center py-5"
      style={{ minHeight: "300px" }}
    >
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">{text}</span>
      </div>
      {text && <div className="mt-2 text-body-tertiary">{text}</div>}
    </div>
  );
}

export default LoadingSpinner;
