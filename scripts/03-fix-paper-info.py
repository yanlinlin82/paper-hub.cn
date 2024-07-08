import os
import sys
import pandas as pd
import django
from lxml import etree

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import Paper

class PaperInfo:
    def __init__(self, xml_node):
        self.xml_node = xml_node
        self._title = None
        self._journal = None
        self._pub_date = None
        self._pub_year = None
        self._doi = None
        self._pmid = None
        self._authors = None
        self._affiliations = None
        self._abstract = None
        self._keywords = None
        self._language = None
        self.labels = []

    @property
    def title(self):
        if self._title is None:
            node_list = self.xml_node.xpath('MedlineCitation/Article/ArticleTitle')
            text = []
            for node in node_list:
                for child in node.itertext(with_tail=True):
                    if isinstance(child, etree._Element):
                        text.append(etree.tostring(child, encoding='unicode', method='html'))
                    else:
                        text.append(child)
            self._title = ''.join(text)
            self._title = self._title.rstrip('.')
        return self._title

    @property
    def journal(self):
        if self._journal is None:
            self._journal = (self.xml_node.xpath('MedlineCitation/Article/Journal/Title/text()') or [''])[0]
        return self._journal

    @property
    def pub_date(self):
        self._parse_date()
        return self._pub_date
    
    @property
    def pub_year(self):
        self._parse_date()
        return self._pub_year

    @property
    def doi(self):
        if self._doi is None:
            self._doi = (self.xml_node.xpath('MedlineCitation/Article/ELocationID[@EIdType="doi"]/text()') or [''])[0]
            self._doi = self._doi.rstrip('.')
        return self._doi

    @property
    def pmid(self):
        if self._pmid is None:
            self._pmid = (self.xml_node.xpath('MedlineCitation/PMID/text()') or [''])[0]
        return self._pmid

    @property
    def authors(self):
        if self._authors is None:
            authors = []
            for item in self.xml_node.xpath('MedlineCitation/Article/AuthorList/Author'):
                try:
                    if item.find('CollectiveName') is not None:
                        authors.append(item.xpath('CollectiveName/text()')[0])
                    elif item.find('ForeName') is not None and item.find('LastName') is not None:
                        authors.append(item.xpath('ForeName/text()')[0] + ' ' + item.xpath('LastName/text()')[0])
                    elif item.find('LastName') is not None:
                        authors.append(item.xpath('LastName/text()')[0])
                    elif item.find('ForeName') is not None:
                        authors.append(item.xpath('ForeName/text()')[0])
                except IndexError:
                    print('IndexError: (author item not processed correctly)', etree.tostring(item), file=sys.stderr)
            self._authors = authors
        return self._authors

    @property
    def affiliations(self):
        if self._affiliations is None:
            affiliations = []
            for item in self.xml_node.xpath('MedlineCitation/Article/AuthorList/Author/AffiliationInfo/Affiliation/text()'):
                affiliations.append(item.strip())
            self._affiliations = affiliations
        return self._affiliations

    @property
    def abstract(self):
        if self._abstract is None:
            node = self.xml_node.xpath('MedlineCitation/Article/Abstract')
            if len(node) == 0:
                self._abstract = ''
            else:
                node = node[0]
                text_nodes = node.xpath('AbstractText[not(@Label)]/text()')
                if len(text_nodes) > 0:
                    self._abstract = ''.join(text_nodes)
                else:
                    sections = node.xpath('AbstractText[@Label]')
                    if len(sections) == 0:
                        self._abstract = ''
                    else:
                        section_text = []
                        for section in sections:
                            text = []
                            text.append(section.get('Label') + ': ')
                            for child in section.itertext(with_tail=True):
                                if isinstance(child, etree._Element):
                                    text.append(etree.tostring(child, encoding='unicode', method='html'))
                                else:
                                    text.append(child)
                            section_text.append(''.join(text))
                        self._abstract = '\n'.join(section_text)
        return self._abstract

    @property
    def keywords(self):
        if self._keywords is None:
            try:
                keywords = []
                for item in self.xml_node.xpath('MedlineCitation/KeywordList/Keyword'):
                    if item is not None and item.text is not None:
                        name = item.text.strip()
                        if name != "" and name not in keywords:
                            keywords.append(name)
                self._keywords = keywords
            except IndexError:
                self._keywords = []
        return self._keywords

    @property
    def language(self):
        if self._language is None:
            self._language = (self.xml_node.xpath('MedlineCitation/Article/Language/text()') or [''])[0]
        return self._language

    def _parse_date(self):
        if self._pub_date is not None:
            return

        node = self.xml_node.xpath('MedlineCitation/Article/Journal/JournalIssue/PubDate')
        if len(node) == 0:
            node = self.xml_node.xpath('MedlineCitation/Article/ArticleDate')

        if len(node) == 0:
            self._pub_date = ''
        else:
            node = node[0]
            # eg. <PubDate><Year>2012</Year><Month>Jan</Month><Day>01</Day></PubDate>
            #     <PubDate><Year>2012</Year><Month>Jan-Feb</Month></PubDate>
            #     <PubDate><MedlineDate>2012 Jan-Feb</MedlineDate></PubDate>
            year = node.xpath('Year/text()')
            month = node.xpath('Month/text()')
            day = node.xpath('Day/text()')
            if len(year) == 0:
                node = node.xpath('MedlineDate/text()')
                if node is None:
                    self._pub_date = ''
                else:
                    # eg. <MedlineDate>2012 Jan-Feb</MedlineDate> or <MedlineDate>2012</MedlineDate>
                    self._pub_date = node[0]
                    self._pub_year = node[0].split(' ')[0]
            else:
                self._pub_date = self._pub_year = year[0]
                if len(month) > 0:
                    self._pub_date += '-' + month[0]
                    if len(day) > 0:
                        self._pub_date += '-' + day[0]

def fix_paper_info(input_xlsx, pubmed_dir):
    df = pd.read_excel(input_xlsx, dtype=str) # id,pmid,doi,journal,pub_year,title,source,index,pmid_from_cache,doi_from_cache,updated

    grouped = {}
    total = 0
    for index, row in df.iterrows():
        if pd.isna(row['source']):
            continue
        if row['source'] not in grouped:
            grouped[row['source']] = {}
        grouped[row['source']][row['index']] = row
        grouped[row['source']][row['index']]['index'] = index
        total += 1

    cnt, updated = 0, 0
    for source in grouped:
        print(f"Processing source: {source}")
        if int(source) <= 1219:
            xml_gz_file = os.path.join(pubmed_dir, 'pubmed', 'baseline', f'pubmed24n{source}.xml.gz')
        else:
            xml_gz_file = os.path.join(pubmed_dir, 'pubmed', 'updatefiles', f'pubmed24n{source}.xml.gz')
        if not os.path.exists(xml_gz_file):
            print(f"Warning: {xml_gz_file} not found")
            continue
        tree = etree.parse(xml_gz_file)
        root = tree.getroot()

        cnt2 = 0
        for index in grouped[source]:
            row = grouped[source][index]
            cnt += 1
            cnt2 += 1
            print(f"Processing ({cnt}/{total}) (src:{source}, {cnt2}): row:{row['index']}, id:{row['id']}, pmid:{row['pmid']}, doi:{row['doi']}, {row['journal']}, {row['pub_year']}, {row['title']}")
            article_node = root.xpath(f'/PubmedArticleSet/PubmedArticle[{int(index)+1}]')
            if len(article_node) == 0:
                print(f"Warning: article node '{source}[{int(index)+1}]' not found in {xml_gz_file}, skip...")
                continue
            paper_info = PaperInfo(article_node[0])
            paper = Paper.objects.get(id=row['id'])
            if paper is not None:
                print(f'Update paper: id={paper.id}')
                any_change = False
                if paper.journal != paper_info.journal:
                    print(f"  journal: '{paper.journal}' -> '{paper_info.journal}'")
                    paper.journal = paper_info.journal
                    any_change = True
                if paper.pub_date != paper_info.pub_date:
                    print(f"  pub_date: '{paper.pub_date}' -> '{paper_info.pub_date}'")
                    paper.pub_date = paper_info.pub_date
                    any_change = True
                if paper.pub_year != paper_info.pub_year:
                    print(f"  pub_year: '{paper.pub_year}' -> '{paper_info.pub_year}'")
                    paper.pub_year = paper_info.pub_year
                    any_change = True
                if paper.title != paper_info.title:
                    print(f"  title: '{paper.title}' -> '{paper_info.title}'")
                    paper.title = paper_info.title
                    any_change = True
                authors = '\n'.join(paper_info.authors)
                if paper.authors != authors:
                    print(f"  authors: '{paper.authors}' -> '{authors}'")
                    paper.authors = authors
                    any_change = True
                affiliations = '\n'.join(paper_info.affiliations)
                if paper.affiliations != affiliations:
                    print(f"  affiliations: '{paper.affiliations}' -> '{affiliations}'")
                    paper.affiliations = affiliations
                    any_change = True
                if paper.abstract != paper_info.abstract:
                    print(f"  abstract: '{paper.abstract}' -> '{paper_info.abstract}'")
                    paper.abstract = paper_info.abstract
                    any_change = True
                keywords = '\n'.join(paper_info.keywords)
                if paper.keywords != keywords:
                    print(f"  keywords: '{paper.keywords}' -> '{keywords}'")
                    paper.keywords = keywords
                    any_change = True
                if paper.doi != paper_info.doi:
                    print(f"  doi: '{paper.doi}' -> '{paper_info.doi}'")
                    paper.doi = paper_info.doi
                    any_change = True
                if paper.pmid != paper_info.pmid:
                    print(f"  pmid: '{paper.pmid}' -> '{paper_info.pmid}'")
                    paper.pmid = paper_info.pmid
                    any_change = True
                if paper.language != paper_info.language:
                    print(f"  language: '{paper.language}' -> '{paper_info.language}'")
                    paper.language = paper_info.language
                    any_change = True
                if any_change:
                    paper.save()
                    print(f"  Updated: {paper}")
                    updated += 1

    print(f"Updated {updated} papers")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: python {sys.argv[0]} <input.xlsx> <pubmed-dir>')
        sys.exit(1)
    input_xlsx = sys.argv[1]
    pubmed_dir = sys.argv[2]
    fix_paper_info(input_xlsx, pubmed_dir)

