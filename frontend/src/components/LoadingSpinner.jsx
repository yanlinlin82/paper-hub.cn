import React from 'react';

function LoadingSpinner({ text = '加载中...' }) {
  return (
    <div className="text-center my-5">
      <div className="spinner-border text-primary" role="status">
        <span className="visually-hidden">{text}</span>
      </div>
      <div className="mt-2 text-muted">{text}</div>
    </div>
  );
}

export default LoadingSpinner;
