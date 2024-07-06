import os
import sys
import pandas as pd
import django
import pickle
import re
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
        self._institutes = None
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
    def institutes(self):
        if self._institutes is None:
            institutes = []
            for item in self.xml_node.xpath('MedlineCitation/Article/AuthorList/Author/AffiliationInfo/Affiliation/text()'):
                institutes.append(item.strip())
            self._institutes = institutes
        return self._institutes

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

    def append_label(self, cond_item):
        if 'label' in cond_item and cond_item['label'] is not None and cond_item['label'] not in self.labels:
            self.labels.append(cond_item['label'])

    def match_keyword(self, cond_item):
        if 'pattern' not in cond_item:
            cond_item['pattern'] = r'\b{}\b'.format(re.escape(cond_item['value']))
        pattern = cond_item['pattern']
        return re.search(pattern, self.title, re.IGNORECASE) \
            or re.search(pattern, self.abstract, re.IGNORECASE) \
            or any(re.search(pattern, k, re.IGNORECASE) for k in self.keywords)

    def match_author(self, author):
        names = [s.lower() for s in author.split() if s]
        if len(names) == 0:
            return False
        for item in self.xml_node.xpath('MedlineCitation/Article/AuthorList/Author'):
            fore_name = (item.xpath('./ForeName/text()') or [''])[0]
            last_name = (item.xpath('./LastName/text()') or [''])[0]
            initials = (item.xpath('./Initials/text()') or [''])[0]

            if fore_name != '' and last_name != '':
                if len(names) == 1:
                    if names[0] == fore_name.lower() or names[0] == last_name.lower():
                        return True
                elif len(names) == 2:
                    if names[0] == fore_name.lower() and names[1] == last_name.lower():
                        return True
                    if names[0] == last_name.lower() and names[1] == fore_name.lower():
                        return True
                else:
                    if author.lower() == fore_name.lower() + ' ' + last_name.lower():
                        return True
                    if author.lower() == last_name.lower() + ' ' + fore_name.lower():
                        return True

                if initials != '':
                    if len(names) == 2:
                        if names[0] == initials.lower() and names[1] == last_name.lower():
                            return True
                        if names[0] == last_name.lower() and names[1] == initials.lower():
                            return True
                    else:
                        if author.lower() == initials.lower() + ' ' + last_name.lower():
                            return True
                        if author.lower() == last_name.lower() + ' ' + initials.lower():
                            return True
            else:
                item_name = ''
                if fore_name != '':
                    item_name = fore_name
                elif last_name != '':
                    item_name = last_name
                elif item.find('CollectiveName') is not None:
                    item_name = (item.xpath('CollectiveName/text()') or [''])[0]

                if item_name != '':
                    pattern = r'\b{}\b'.format(re.escape(author))
                    if re.search(pattern, item_name, re.IGNORECASE):
                        return True
        return False

    def match_institute(self, institute):
        patterns = [r'\b{}\b'.format(re.escape(n)) for n in institute.split() if n]
        if len(patterns) != 0:
            for i in self.institutes:
                if all(re.search(p, i, re.IGNORECASE) for p in patterns):
                    return True
        return False

    def match_journal(self, journal):
        query = ' '.join([s for s in journal.split() if s])
        pattern = r'\b{}\b'.format(re.escape(query))
        return re.search(pattern, self.journal, re.IGNORECASE)

    def match_cite(self, cite):
        return cite in self.xml_node.xpath('PubmedData/ReferenceList/Reference/ArticleIdList/ArticleId[@IdType="pubmed"]/text()')

    def match(self, cond):
        if cond is None or len(cond) == 0:
            return True, []
        matched = False
        labels = []
        for cond_item in cond:
            if cond_item['type'] == 'keyword':
                if self.match_keyword(cond_item):
                    matched = True
                    self.append_label(cond_item)
            elif cond_item['type'] == 'author':
                if self.match_author(cond_item['value']):
                    matched = True
                    self.append_label(cond_item)
            elif cond_item['type'] == 'institute':
                if self.match_institute(cond_item['value']):
                    matched = True
                    self.append_label(cond_item)
            elif cond_item['type'] == 'journal':
                if self.match_journal(cond_item['value']):
                    matched = True
                    self.append_label(cond_item)
            elif cond_item['type'] == 'cite':
                if self.match_cite(cond_item['value']):
                    matched = True
                    self.append_label(cond_item)
        return matched, labels

class Database:
    def __init__(self, db_xml_gz):
        self.tree = etree.parse(db_xml_gz)
        self.root = self.tree.getroot()

    def list_papers(self, cond):
        papers = []
        for article_node in self.root.xpath('/PubmedArticleSet/PubmedArticle'):
            paper = Paper(article_node)
            if paper.title == '':
                continue # some non-English articles have no title
            if cond is None:
                papers.append(paper)
            else:
                matched, labels = paper.match(cond)
                if matched:
                    if labels is not None and len(labels) > 0:
                        paper.labels.extend(labels)
                    papers.append(paper)
        return papers

class PubmedIndex:
    def __init__(self, pubmed_dir):
        self.pubmed_dir = pubmed_dir
        self.loaded = False
        self.data = {'doi':{}, 'pmid':{}}
        self.pickle_file = 'cache/pubmed-index.pkl'

    def _load(self):
        print(f'Loading PubMed index from {self.pubmed_dir} ...', file=sys.stderr)
        self.data = {'doi':{}, 'pmid':{}}
        files = sorted(os.listdir(os.path.join(self.pubmed_dir, 'cache', 'id-list')))
        cnt, total = 0, len(files)
        for file in files:
            cnt += 1
            print(f'  Loading file {cnt}/{total}: {file} ...\r', end='', file=sys.stderr)
            if file.endswith('.tsv'):
                with open(os.path.join(self.pubmed_dir, 'cache', 'id-list', file), 'r') as f:
                    for line in f:
                        source, index, doi, pmid = line.strip().split('\t')
                        self.data['doi'][doi] = { 'source': source, 'index': index, 'pmid': pmid }
                        self.data['pmid'][pmid] = { 'source': source, 'index': index, 'doi': doi }
        print(f"Loaded {len(self.data['doi'])} DOI records and {len(self.data['pmid'])} PMID records.", file=sys.stderr)

    def ensure_load(self):
        if not self.loaded:
            if os.path.exists(self.pickle_file):
                print('Loading PubMed index from cache/pubmed-index.pkl ...', file=sys.stderr)
                with open(self.pickle_file, 'rb') as f:
                    self.data = pickle.load(f)
                print(f"Loaded {len(self.data['doi'])} DOI records and {len(self.data['pmid'])} PMID records.", file=sys.stderr)
            else:
                self._load()
                with open('cache/pubmed-index.pkl', 'wb') as f:
                    pickle.dump(self.data, f)
            self.loaded = True

    def get_article_node(self, source, index):
        if int(source) <= 1219:
            xml_gz_file = os.path.join(self.pubmed_dir, 'pubmed', 'baseline', f'pubmed24n{source}.xml.gz')
        else:
            xml_gz_file = os.path.join(self.pubmed_dir, 'pubmed', 'updatefiles', f'pubmed24n{source}.xml.gz')
        if not os.path.exists(xml_gz_file):
            print(f'  XML file {xml_gz_file} not found, skip...', file=sys.stderr)
            return None
        tree = etree.parse(xml_gz_file)
        root = tree.getroot()
        article_node = root.xpath(f'/PubmedArticleSet/PubmedArticle[{int(index)+1}]')
        if len(article_node) == 0:
            print(f'  article {int(index)+1} not found in XML file, skip...', file=sys.stderr)
            return None
        return article_node[0]

    def get_paper_info(self, id, source=None, index=None):
        if source is None or index is None:
            self.ensure_load()
            if id in self.data['doi']:
                source = self.data['doi'][id]['source']
                index = self.data['doi'][id]['index']
            elif id in self.data['pmid']:
                source = self.data['pmid'][id]['source']
                index = self.data['pmid'][id]['index']
            else:
                print(f'  paper {id} not found in PubMed index, skip...', file=sys.stderr)
                return

        print(f'  processing paper {id} in {source} with index {index}...', file=sys.stderr)
        article_node = self.get_article_node(source, index)

        return PaperInfo(article_node)

def main():
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <pubmed-dir> [doi|pmid] [source] [index]')
        sys.exit(1)

    pubmed_dir = sys.argv[1]
    id = None if len(sys.argv) < 3 else sys.argv[2]
    source = None if len(sys.argv) < 4 else sys.argv[3]
    index = None if len(sys.argv) < 5 else sys.argv[4]

    pubmed_index = PubmedIndex(pubmed_dir)
    if id is not None:
        paper_info = pubmed_index.get_paper_info(id, source, index)
        print(f'  title: {paper_info.title}')
        print(f'  journal: {paper_info.journal}')
        print(f'  pub_date: {paper_info.pub_date}')
        print(f'  pub_year: {paper_info.pub_year}')
        print(f'  DOI: {paper_info.doi}')
        print(f'  PMID: {paper_info.pmid}')
        print(f'  authors: {paper_info.authors}')
        print(f'  institutes: {paper_info.institutes}')
        print(f'  abstract: {paper_info.abstract}')
        print(f'  keywords: {paper_info.keywords}')
        print(f'  language: {paper_info.language}')
    else:
        cnt, total = 0, Paper.objects.count()
        for paper in Paper.objects.all().order_by('id'):
            cnt += 1
            print('=' * 80, file=sys.stderr)
            print(f'Processing ({cnt}/{total}) paper {paper.id}: {paper.title}...', file=sys.stderr)

            if paper.doi == '' and paper.pmid == '':
                print(f'  paper {paper.id} has no DOI or PMID, skip...', file=sys.stderr)
                continue

            if paper.pmid != '':
                print(f'  process paper {paper.id} with PMID: {paper.pmid}...', file=sys.stderr)
                paper_info = pubmed_index.get_paper_info(paper.pmid)
            else:
                print(f'  process paper {paper.id} with DOI: {paper.doi}...', file=sys.stderr)
                paper_info = pubmed_index.get_paper_info(paper.doi)

            if paper_info is not None:
                print(f'paper.id: {paper.id}', file=sys.stderr)
                if paper_info.title.lower() != paper.title.lower():
                    print(f'title mismatched, skipped:\n  [OLD]: {paper.title}\n  [NEW]: {paper_info.title}', file=sys.stderr)
                    continue
                if paper.pmid != '' and paper_info.pmid != paper.pmid:
                    print(f'PMID mismatched, skipped:\n  [OLD]: {paper.pmid}\n  [NEW]: {paper_info.pmid}', file=sys.stderr)
                    continue
                if paper.doi != '' and paper_info.doi != paper.doi:
                    print(f'DOI mismatched, skipped:\n  [OLD]: {paper.doi}\n  [NEW]: {paper_info.doi}', file=sys.stderr)
                    continue
                paper.title = paper_info.title
                paper.journal = paper_info.journal
                paper.pub_date = paper_info.pub_date
                paper.pub_year = paper_info.pub_year
                paper.doi = paper_info.doi
                paper.pmid = paper_info.pmid
                paper.authors = ', '.join(paper_info.authors)
                paper.institutes = ', '.join(paper_info.institutes)
                paper.abstract = paper_info.abstract
                paper.keywords = ', '.join(paper_info.keywords)
                paper.language = paper_info.language
                paper.save()

if __name__ == '__main__':
    main()
