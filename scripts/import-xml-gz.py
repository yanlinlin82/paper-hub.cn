import os
import sys
import django
from lxml import etree

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from core.models import Paper, PaperReference, PubMedIndex
from core.paper import PaperInfo

def J(s):
    return ', '.join(s.split('\n'))

def update_references(paper, paper_info, type):
    cc_list = paper_info.get_references(type)
    print(f"  {type} for paper ({paper.pk}): {len(cc_list)}")
    total, new, updated, deleted = len(cc_list), 0, 0, 0
    if cc_list:
        pr_list = PaperReference.objects.filter(paper=paper, type=type).order_by('index')
        pr_cnt = pr_list.count()
        for index, cc in enumerate(cc_list):
            if index < pr_cnt:
                pr = pr_list[index]
                any_change = False
                if pr.index != index + 1:
                    print(f"    [{index+1}] index: {pr.index} -> {index + 1}")
                    pr.index = index + 1
                    any_change = True
                ref_type = cc.get('ref_type', '') or ''
                if pr.ref_type != ref_type:
                    print(f"    [{index+1}] ref_type: '{pr.ref_type}' -> '{ref_type}'")
                    pr.ref_type = ref_type
                    any_change = True
                citation = cc.get('citation', '') or ''
                if pr.citation != citation:
                    print(f"    [{index+1}] citation: '{pr.citation}' -> '{citation}'")
                    pr.citation = citation
                    any_change = True
                doi = cc.get('doi', '') or ''
                if pr.doi != doi:
                    print(f"    [{index+1}] doi: '{pr.doi}' -> '{doi}'")
                    pr.doi = doi
                    any_change = True
                pmid = cc.get('pmid', '') or ''
                if pr.pmid != pmid:
                    print(f"    [{index+1}] pmid: '{pr.pmid}' -> '{pmid}'")
                    pr.pmid = pmid
                    any_change = True
                pmcid = cc.get('pmcid', '') or ''
                if pr.pmcid != pmcid:
                    print(f"    [{index+1}] pmcid: '{pr.pmcid}' -> '{pmcid}'")
                    pr.pmcid = pmcid
                    any_change = True
                if any_change:
                    pr.save()
                    updated += 1
            else:
                print(f"    [{index+1}] New reference {cc}")
                pr = PaperReference(
                    paper=paper,
                    type=type,
                    ref_type=cc.get('ref_type', '') or '',
                    index=index + 1,
                    citation=cc.get('citation', '') or '',
                    doi=cc.get('doi', '') or '',
                    pmid=cc.get('pmid', '') or '',
                    pmcid=cc.get('pmcid', '') or '',
                )
                pr.save()
                new += 1
        if total < pr_cnt:
            deleted = pr_cnt - total
            pr_list.filter(index__gt=total).delete()
        print(f"  {type} for paper ({paper.pk}): {total} total, {new} new, {updated} updated, {deleted} deleted")

def process_article(source, index, article_node, removed_pmids):
    paper_info = PaperInfo(article_node)
    if paper_info.pmid in removed_pmids:
        print(f"Skip removed PMID: {paper_info.pmid}")
        return

    if not PubMedIndex.objects.filter(source=source, index=index).exists():
        PubMedIndex.objects.create(source=source, index=index, pmid=paper_info.pmid, doi=paper_info.doi)
        print(f"Added PubMedIndex record: source {source}, index {index}, pmid {paper_info.pmid}, doi {paper_info.doi}")

    if paper_info.pmid is not None:
        if Paper.objects.filter(pmid=paper_info.pmid).exists():
            paper = Paper.objects.get(pmid=paper_info.pmid)
            print(f"Select paper ({paper.pk}) for PMID {paper_info.pmid} to update")
        else:
            paper = Paper(pmid=paper_info.pmid)
            paper.save()
            print(f"Create paper ({paper.pk}) for PMID {paper_info.pmid}")
    elif paper_info.doi is not None:
        if Paper.objects.filter(doi=paper_info.doi).exists():
            paper = Paper.objects.get(doi=paper_info.doi)
            print(f"Select paper ({paper.pk}) for DOI {paper_info.doi} to update")
        else:
            paper = Paper(doi=paper_info.doi)
            print(f"Create paper ({paper.pk}) for DOI {paper_info.doi}")
    else:
        paper = Paper()
        paper.save()
        print(f"Create paper ({paper.pk})")

    any_change = False
    if paper_info.journal is not None:
        if paper.journal != paper_info.journal:
            print(f"  journal: '{paper.journal}' -> '{paper_info.journal}'")
            paper.journal = paper_info.journal
            any_change = True
    if paper_info.pub_date is not None:
        if paper.pub_date != paper_info.pub_date:
            print(f"  pub_date: '{paper.pub_date}' -> '{paper_info.pub_date}'")
            paper.pub_date = paper_info.pub_date
            any_change = True
    if paper_info.pub_year is not None:
        if paper.pub_year != paper_info.pub_year:
            print(f"  pub_year: '{paper.pub_year}' -> '{paper_info.pub_year}'")
            paper.pub_year = paper_info.pub_year
            any_change = True
    if paper_info.title is not None:
        if paper.title != paper_info.title:
            print(f"  title: '{paper.title}' -> '{paper_info.title}'")
            paper.title = paper_info.title
            any_change = True
    if paper_info.authors is not None:
        authors = '\n'.join(paper_info.authors)
        if paper.authors != authors:
            print(f"  authors: '{J(paper.authors)}' -> '{J(authors)}'")
            paper.authors = authors
            any_change = True
    if paper_info.affiliations is not None:
        affiliations = '\n'.join(paper_info.affiliations)
        if paper.affiliations != affiliations:
            print(f"  affiliations: '{J(paper.affiliations)}' -> '{J(affiliations)}'")
            paper.affiliations = affiliations
            any_change = True
    if paper_info.abstract is not None:
        if paper.abstract != paper_info.abstract:
            print(f"  abstract: '{J(paper.abstract)}' -> '{J(paper_info.abstract)}'")
            paper.abstract = paper_info.abstract
            any_change = True
    if paper_info.keywords is not None:
        keywords = '\n'.join(paper_info.keywords)
        if paper.keywords != keywords:
            print(f"  keywords: '{J(paper.keywords)}' -> '{J(keywords)}'")
            paper.keywords = keywords
            any_change = True
    if paper_info.doi is not None:
        if paper.doi != paper_info.doi:
            print(f"  doi: '{paper.doi}' -> '{paper_info.doi}'")
            paper.doi = paper_info.doi
            any_change = True
    if paper_info.pmid is not None:
        if paper.pmid != paper_info.pmid:
            print(f"  pmid: '{paper.pmid}' -> '{paper_info.pmid}'")
            paper.pmid = paper_info.pmid
            any_change = True
    if paper_info.arxiv_id is not None:
        if paper.arxiv_id != paper_info.arxiv_id:
            print(f"  arxiv_id: '{paper.arxiv_id}' -> '{paper_info.arxiv_id}'")
            paper.arxiv_id = paper_info.arxiv_id
            any_change = True
    if paper_info.pmcid is not None:
        if paper.pmcid != paper_info.pmcid:
            print(f"  pmcid: '{paper.pmcid}' -> '{paper_info.pmcid}'")
            paper.pmcid = paper_info.pmcid
            any_change = True
    if paper_info.cnki_id is not None:
        if paper.cnki_id != paper_info.cnki_id:
            print(f"  cnki_id: '{paper.cnki_id}' -> '{paper_info.cnki_id}'")
            paper.cnki_id = paper_info.cnki_id
            any_change = True
    if paper_info.language is not None:
        if paper.language != paper_info.language:
            print(f"  language: '{paper.language}' -> '{paper_info.language}'")
            paper.language = paper_info.language
            any_change = True
    if any_change:
        paper.save()
        print(f"  Saved paper ({paper.pk})")
    else:
        print(f"  No change for paper ({paper.pk})")

    update_references(paper, paper_info, 'CommentsCorrectionsList')
    update_references(paper, paper_info, 'ReferenceList')


def import_xml_gz(pubmed_dir, source, index=None):
    pubmed_part = 'baseline' if source < 1220 else 'updatefiles'
    pubmed_xml_gz = os.path.join(pubmed_dir, pubmed_part, f'pubmed24n{source}.xml.gz')
    if not os.path.exists(pubmed_xml_gz):
        print(f"File not found: {pubmed_xml_gz}")
        return

    print(f"Processing {pubmed_xml_gz}")
    tree = etree.parse(pubmed_xml_gz)
    root = tree.getroot()

    removed_pmids = set()
    for pmid in root.xpath('/PubmedArticleSet/DeleteCitation/PMID/text()'):
        removed_pmids.add(int(pmid))

    if index is not None:
        article_node = root.xpath(f'/PubmedArticleSet/PubmedArticle[{index}]')[0]
        process_article(source, index, article_node, removed_pmids)
    else:
        for pmid in removed_pmids:
            if PubMedIndex.objects.filter(pmid=pmid).exists():
                PubMedIndex.objects.filter(pmid=pmid).delete()
                print(f"Deleted PMID {pmid} from PubMedIndex")
        for index, article_node in enumerate(root.xpath('/PubmedArticleSet/PubmedArticle')):
            process_article(source, index, article_node, removed_pmids)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: python {sys.argv[0]} <pubmed-dir> <source> [index]')
        sys.exit(1)

    pubmed_dir = sys.argv[1]
    source = int(sys.argv[2])
    index = int(sys.argv[3]) if len(sys.argv) > 3 else None
    if source < 1:
        print("Invalid source")
        sys.exit(1)
    if index is not None:
        if index < 1:
            print("Invalid index")
            sys.exit(1)
    import_xml_gz(pubmed_dir, source, index)
