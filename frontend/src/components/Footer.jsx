import React from 'react';

function Footer() {
  return (
    <footer className="bg-secondary text-white text-center py-3">
      <div className="py-2">
        <a className="link-light external-link" href="https://yanlinlin.cn/" target="_blank" rel="noreferrer">
          &copy; 2022 - 2024
        </a>{' '}
        |{' '}
        <a className="link-light external-link" href="http://beian.miit.gov.cn/" target="_blank" rel="noreferrer">
          京ICP备18031542号-9
        </a>{' '}
        |{' '}
        <a className="link-light external-link" href="https://github.com/yanlinlin82/paper-hub.cn/" target="_blank" rel="noreferrer">
          GitHub
        </a>
      </div>
      <div className="py-1">
        基于 <a className="link-light external-link" href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">Django</a>{' '}
        和 <a className="link-light external-link" href="https://getbootstrap.com/" target="_blank" rel="noreferrer">Bootstrap</a> 和{' '}
        <a className="link-light external-link" href="https://react.dev/" target="_blank" rel="noreferrer">React</a> 开发
      </div>
    </footer>
  );
}

export default Footer;
