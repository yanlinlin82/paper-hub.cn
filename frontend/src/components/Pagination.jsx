import React from 'react';
import { useSearchParams } from 'react-router-dom';

function Pagination({ paginator }) {
  const [searchParams, setSearchParams] = useSearchParams();

  if (!paginator || paginator.num_pages <= 1) return null;

  const goToPage = (page) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', page.toString());
    setSearchParams(newParams);
  };

  const { number: currentPage, num_pages: totalPages, has_previous, has_next, previous_page_number, next_page_number } = paginator;

  const pages = [];
  for (let i = 1; i <= totalPages; i++) {
    if (
      i === 1 ||
      i === totalPages ||
      (i >= currentPage - 2 && i <= currentPage + 2)
    ) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== '...') {
      pages.push('...');
    }
  }

  return (
    <nav aria-label="Page navigation">
      <ul className="pagination justify-content-center">
        {has_previous && (
          <li className="page-item">
            <button className="page-link" onClick={() => goToPage(previous_page_number)}>
              &laquo; 上一页
            </button>
          </li>
        )}
        {pages.map((page, idx) =>
          page === '...' ? (
            <li key={`ellipsis-${idx}`} className="page-item disabled">
              <span className="page-link">...</span>
            </li>
          ) : (
            <li key={page} className={`page-item ${page === currentPage ? 'active' : ''}`}>
              <button className="page-link" onClick={() => goToPage(page)}>
                {page}
              </button>
            </li>
          )
        )}
        {has_next && (
          <li className="page-item">
            <button className="page-link" onClick={() => goToPage(next_page_number)}>
              下一页 &raquo;
            </button>
          </li>
        )}
      </ul>
    </nav>
  );
}

export default Pagination;
