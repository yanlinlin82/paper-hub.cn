import React from 'react';
import { Link } from 'react-router-dom';

function PaperInfo({ paper, groupName }) {
  if (!paper) return null;

  return (
    <div className="text-start">
      {paper.journal_impact_factor && paper.journal_impact_factor_quartile && (
        <>
          <span className="journal-if">IF:{paper.journal_impact_factor}</span>
          <span className={`journal-q${paper.journal_impact_factor_quartile}`}>
            Q{paper.journal_impact_factor_quartile}
          </span>
        </>
      )}
      {paper.journal && (
        <Link
          to={`/group/${groupName}/journal/${encodeURIComponent(paper.journal)}`}
        >
          <i>{paper.journal}</i>
        </Link>
      )}
      , {paper.pub_date}.
      {paper.doi && (
        <>
          {' '}DOI:{' '}
          <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noreferrer" className="external-link">
            {paper.doi}
          </a>
        </>
      )}
      {paper.pmid && (
        <>
          {' '}PMID:{' '}
          <a href={`https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}`} target="_blank" rel="noreferrer" className="external-link">
            {paper.pmid}
          </a>
        </>
      )}
      {paper.pmcid && (
        <>
          {' '}PMCID:{' '}
          <a href={`http://www.ncbi.nlm.nih.gov/pmc/articles/${paper.pmcid}`} target="_blank" rel="noreferrer" className="external-link">
            {paper.pmcid}
          </a>
        </>
      )}
      {paper.arxiv_id && (
        <>
          {' '}arXiv:{' '}
          <a href={`https://arxiv.org/abs/${paper.arxiv_id}`} target="_blank" rel="noreferrer" className="external-link">
            {paper.arxiv_id}
          </a>
        </>
      )}
      {paper.cnki_id && (
        <>
          {' '}CNKI:{' '}
          <a
            href={`https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&filename=${paper.cnki_id}`}
            target="_blank"
            rel="noreferrer"
            className="external-link"
          >
            {paper.cnki_id}
          </a>
        </>
      )}
    </div>
  );
}

export default PaperInfo;
