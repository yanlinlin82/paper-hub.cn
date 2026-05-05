import React from "react";

function LoadingSpinner({ text = "加载中..." }) {
  return (
    <div className="loading-container">
      <div className="loading-spinner" />
      <div className="loading-text">{text}</div>
    </div>
  );
}

export default LoadingSpinner;
