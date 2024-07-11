import os
import sys
import requests
import json
import xmltodict
import re
import zoneinfo
from datetime import datetime, timedelta
from django.urls import reverse
from django.db.models import Count
from django.db.models.aggregates import Min
from core.models import CustomCheckInInterval, PubMedIndex, Paper
from paperhub import settings
import requests
from lxml import etree
import pandas as pd

class PaperInfo:
    def __init__(self, xml_node=None):
        self.xml_node = xml_node
        self._title = None
        self._journal = None
        self._pub_date = None
        self._pub_year = None
        self._doi = None
        self._pmid = None
        self._arxiv_id = None
        self._pmcid = None
        self._cnki_id = None
        self._authors = None
        self._affiliations = None
        self._abstract = None
        self._keywords = None
        self._urls = None
        self._language = None
        self.labels = []

    @property
    def title(self):
        if self._title is None:
            if self.xml_node is not None:
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
            if self.xml_node is not None:
                self._journal = (self.xml_node.xpath('MedlineCitation/Article/Journal/Title/text()') or [None])[0]
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
            if self.xml_node is not None:
                self._doi = (self.xml_node.xpath('MedlineCitation/Article/ELocationID[@EIdType="doi"]/text()') or [None])[0]
                if self._doi is not None:
                    self._doi = self._doi.rstrip('.')
        if self._doi is None:
            if self.xml_node is not None:
                self._doi = (self.xml_node.xpath('PubmedData/ArticleIdList/ArticleId[@IdType="doi"]/text()') or [None])[0]
                if self._doi is not None:
                    self._doi = self._doi.rstrip('.')
        return self._doi

    @property
    def pmid(self):
        if self._pmid is None:
            if self.xml_node is not None:
                self._pmid = (self.xml_node.xpath('MedlineCitation/PMID/text()') or [None])[0]
        if self._pmid is None:
            if self.xml_node is not None:
                self._pmid = (self.xml_node.xpath('PubmedData/ArticleIdList/ArticleId[@IdType="pubmed"]/text()') or [None])[0]
        return self._pmid

    @property
    def authors(self):
        if self._authors is None:
            if self.xml_node is not None:
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
            if self.xml_node is not None:
                affiliations = []
                for item in self.xml_node.xpath('MedlineCitation/Article/AuthorList/Author/AffiliationInfo/Affiliation/text()'):
                    affiliations.append(item.strip())
                self._affiliations = affiliations
        return self._affiliations

    @property
    def abstract(self):
        if self._abstract is None:
            if self.xml_node is not None:
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
            if self.xml_node is not None:
                keywords = []
                for item in self.xml_node.xpath('MedlineCitation/KeywordList/Keyword'):
                    if item is not None and item.text is not None:
                        name = item.text.strip()
                        if name != "" and name not in keywords:
                            keywords.append(name)
                self._keywords = keywords
        return self._keywords

    @property
    def language(self):
        if self._language is None:
            if self.xml_node is not None:
                self._language = (self.xml_node.xpath('MedlineCitation/Article/Language/text()') or [None])[0]
        return self._language

    @property
    def urls(self):
        if self._urls is None:
            url = []
            if self.doi:
                url.append(f"https://doi.org/{self.doi}")
            if self.pmid:
                url.append(f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/")
            self._urls = url
        return self._urls

    @property
    def arxiv_id(self):
        return self._arxiv_id

    @property
    def pmcid(self):
        if self._pmcid is None:
            if self.xml_node is not None:
                self._pmcid = (self.xml_node.xpath('PubmedData/ArticleIdList/ArticleId[@IdType="pmc"]/text()') or [None])[0]
        return self._pmcid

    @property
    def cnki_id(self):
        return self._cnki_id

    def _parse_date(self):
        if self._pub_date is None:
            if self.xml_node is not None:
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
                            self._pub_year = int(node[0].split(' ')[0])
                    else:
                        self._pub_date = self._pub_year = year[0]
                        self._pub_year = int(self._pub_year)
                        if len(month) > 0:
                            self._pub_date += '-' + month[0]
                            if len(day) > 0:
                                self._pub_date += '-' + day[0]
        if self._pub_year is None:
            if self._pub_date:
                self._pub_year = node[0].split(' ')[0]
                self._pub_year = int(self._pub_year)

    def get_references(self, type = 'ReferenceList'): # ReferenceList, CommentsCorrectionsList
        references = []
        if self.xml_node is not None:
            if type == 'ReferenceList':
                for item in self.xml_node.xpath('PubmedData/ReferenceList/Reference'):
                    ref = {}
                    ref['ref_type'] = 'Reference'
                    ref['citation'] = item.xpath('Citation/text()' or [None])[0]
                    ref['doi'] = (item.xpath('ArticleIdList/ArticleId[@IdType="doi"]/text()') or [None])[0]
                    ref['pmid'] = (item.xpath('ArticleIdList/ArticleId[@IdType="pubmed"]/text()') or [None])[0]
                    ref['pmcid'] = (item.xpath('ArticleIdList/ArticleId[@IdType="pmcid"]/text()') or [None])[0]
                    references.append(ref)
            elif type == 'CommentsCorrectionsList':
                for item in self.xml_node.xpath('MedlineCitation/CommentsCorrectionsList/CommentsCorrections'):
                    ref = {}
                    ref['ref_type'] = item.get('RefType')
                    ref['citation'] = (item.xpath('RefSource/text()') or [None])[0]
                    ref['pmid'] = (item.xpath('PMID/text()') or [None])[0]
                    references.append(ref)
            else:
                print(f"Error: Unknown type '{type}'")
        return references

    def __str__(self):
        return f"<{self.journal}, {self.pub_year}, {self.title}>"

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
                        print(f"  authors: '{paper.authors}' -> '{authors}'")
                        paper.authors = authors
                        any_change = True
                if paper_info.affiliations is not None:
                    affiliations = '\n'.join(paper_info.affiliations)
                    if paper.affiliations != affiliations:
                        print(f"  affiliations: '{paper.affiliations}' -> '{affiliations}'")
                        paper.affiliations = affiliations
                        any_change = True
                if paper_info.abstract is not None:
                    if paper.abstract != paper_info.abstract:
                        print(f"  abstract: '{paper.abstract}' -> '{paper_info.abstract}'")
                        paper.abstract = paper_info.abstract
                        any_change = True
                if paper_info.keywords is not None:
                    keywords = '\n'.join(paper_info.keywords)
                    if paper.keywords != keywords:
                        print(f"  keywords: '{paper.keywords}' -> '{keywords}'")
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
                    print(f"  Updated: {paper}")
                    updated += 1

    print(f"Updated {updated} papers")

def convert_string_to_datetime(s):
    format_strings = [
        '%Y-%m-%d %H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M',
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d-%b-%Y',
        '%Y %b %d',
        '%b %d, %Y',
        '%d %b, %Y',
        '%Y %b',
        '%Y'
    ]
    for format_string in format_strings:
        try:
            dt = datetime.strptime(s, format_string)
            return dt
        except ValueError:
            pass  # continue to the next format string
    return None

def extract_date_and_year_from_dict(data, key):
    if key not in data:
        return None, None
    dt = convert_string_to_datetime(data[key])
    if dt is None:
        return None, None
    return dt, dt.year

def fetch_and_cache(url, cache_filename):
    if os.path.exists(cache_filename):
        # If the cache file exists, load the data from it
        with open(cache_filename, 'r', encoding='utf-8') as cache_file:
            data = cache_file.read()
        print(f"Loaded data from cache '{cache_filename}'", file=sys.stderr)
    else:
        # If the cache file doesn't exist, fetch data from the URL
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text
            # Cache the data to a local file
            os.makedirs(os.path.dirname(cache_filename), mode=0o775, exist_ok=True)
            with open(cache_filename, 'w', encoding='utf-8') as cache_file:
                cache_file.write(data)
            print(f"Fetched data from the URL and cached it: {url}", file=sys.stderr)
        else:
            print(f"Failed to fetch data from the URL: {url} (status={response.status_code})", file=sys.stderr)
            data = None
    return data

def fetch_json(api_url, cache_filename, is_xml=False):
    txt = fetch_and_cache(api_url, cache_filename)
    if txt is not None:
        try:
            if is_xml:
                return xmltodict.parse(txt)
            else:
                return json.loads(txt)
        except:
            print(f"Error parsing JSON/XML: {txt}", file=sys.stderr)
            return None
    return None

# Function to query paper info by arXiv ID
def get_paper_info_by_arxiv_id(arxiv_id):
    cache_filename = os.path.join(settings.BASE_DIR, "cache/arxiv/" + arxiv_id + ".txt")
    api_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    data = fetch_json(api_url, cache_filename, is_xml=True)
    if 'feed' in data and 'entry' in data['feed']:
        obj = data['feed']['entry']
        pub_date, pub_year = extract_date_and_year_from_dict(obj, 'published')
        paper_info = {
            'id': {
                'doi': f"10.48550/arXiv.{arxiv_id}",
                'arxiv_id': arxiv_id,
            },
            'title': obj.get('title', '') or '',
            'journal': 'arXiv',
            'abstract': obj.get('summary', '') or '',
            'pub_date': pub_date,
            'pub_year': pub_year,
            'authors': [node.get('name') for node in obj.get('author', [])],
            'urls': [obj.get('id')],
        }
        return paper_info, data
    return None, f"Query arXiv ID '{arxiv_id}' failed!"

def parse_elocation(s):
    pattern = re.compile(r'(pii|doi):\s*([^\s]+)\s*')
    return dict(pattern.findall(s))

# Function to query paper info by PubMed ID (PMID)
def get_paper_info_by_pmid(pmid):
    cache_filename = os.path.join(settings.BASE_DIR, "cache/pubmed/" + pmid + ".txt")
    print(f'cache filename: {cache_filename}')
    api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    data = fetch_json(api_url, cache_filename)
    if 'result' in data and pmid in data['result']:
        obj = data['result'][pmid]
        pub_date, pub_year = extract_date_and_year_from_dict(obj, 'pubdate')
        paper_info = {
            'id': {'pmid': pmid},
            'title': obj.get('title', '') or '',
            'journal': obj.get('fulljournalname', '') or '',
            'pub_date': pub_date,
            'pub_year': pub_year,
            'issue': obj.get('issue'),
            'volume': obj.get('volume'),
            'page': obj.get('pages'),
            'abstract': '',
            'authors': [node.get('name') for node in obj.get('authors', [])],
            'urls': [f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"],
        }

        elocations = parse_elocation(obj.get('elocationid'))
        if 'doi' in elocations:
            paper_info['id']['doi'] = elocations['doi']
        if 'pii' in elocations:
            paper_info['id']['pii'] = elocations['pii']

        return paper_info, data
    return None, f"Query PubMed ID '{pmid}' failed!"

# Function to query paper info by PMC ID
def get_paper_info_by_pmcid(pmcid):
    cache_filename = os.path.join(settings.BASE_DIR, "cache/pmc/" + pmcid + ".txt")
    api_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmcid}&format=json"
    data = fetch_json(api_url, cache_filename)
    paper_info = None
    if 'records' in data and len(data['records']) > 0:
        obj = data['records'][0]
        raw_data = {'pmc': data}

        if 'doi' in obj:
            paper_info, doi_data = get_paper_info_by_doi(obj['doi'])
            raw_data['doi'] = doi_data
        elif 'pmid' in obj:
            paper_info, pmid_data = get_paper_info_by_pmid(obj['pmid'])
            raw_data['pmid'] = pmid_data

        if 'pmcid' in data['records'][0]:
            paper_info['id']['pmcid'] = data['records'][0]['pmcid']
        if 'pmid' in data['records'][0]:
            paper_info['id']['pmid'] = data['records'][0]['pmid']
        if 'doi' in data['records'][0]:
            paper_info['id']['doi'] = data['records'][0]['doi']

    if paper_info is None:
        return None, f"Query PMC ID '{pmcid}' failed!"
    else:
        return paper_info, raw_data

# Function to query paper info by DOI
def get_paper_info_by_doi(doi):
    cache_filename = os.path.join(settings.BASE_DIR, "cache/doi/" + doi + ".txt")
    api_url = f"https://api.crossref.org/works/{doi}"
    data = fetch_json(api_url, cache_filename)
    if data is not None and 'message' in data:
        obj = data['message']
        type = obj.get('type', '') or ''
        title = " ".join(obj.get('title', []))
        journal = " ".join(obj.get('container-title', []))
        if 'created' in obj:
            pub_date, pub_year = extract_date_and_year_from_dict(obj['created'], 'date-time')
        issue = obj.get('issue', '') or ''
        volume = obj.get('volume', '') or ''
        page = obj.get('page', '') or ''
        abstract = obj.get('abstract', '') or ''

        paper_info = {
            'id': {'doi': doi},
            'type': type,
            'title': title,
            'journal': journal,
            'pub_date': pub_date,
            'pub_year': pub_year,
            'issue': issue,
            'volume': volume,
            'page': page,
            'abstract': abstract,
            'authors': [(node.get('given', '') or '') + ' ' + (node.get('family', '') or '').strip() for node in obj.get('author', [])],
            'urls': list(dict.fromkeys([node["URL"] for node in obj.get('link', [])]))
        }
        return paper_info, data
    return None, f"Query DOI '{doi}' failed!"

def guess_identifier_type(identifier):
    if identifier.startswith("10."):
        pattern_arxiv = re.compile('^10\.48550\/arXiv\.([0-9]+\.[0-9]+)$')
        m = pattern_arxiv.match(identifier)
        if m:
            return "arxiv_id", m.group(1)
        else:
            return "doi", identifier
    elif re.match(r'^(arXiv:)?\d{4}\.\d{5}$', identifier):
        return "arxiv_id", identifier.replace("arXiv:", "")
    elif identifier.isdigit():
        return "pmid", identifier
    elif identifier.startswith("PMC"):
        return "pmcid", identifier
    else:
        return "unknown", identifier

def get_paper_info_new(identifier, identifier_type):
    source, index = None, None
    if identifier_type == "doi":
        pubmed_index = PubMedIndex.objects.filter(doi=identifier)
        if pubmed_index.count() > 0:
            source = pubmed_index[0].source
            index = pubmed_index[0].index
    elif identifier_type == "pmid":
        pubmed_index = PubMedIndex.objects.filter(pmid=identifier)
        if pubmed_index.count() > 0:
            source = pubmed_index[0].source
            index = pubmed_index[0].index

    if source and index:
        print(f"Will try to fetch paper info from source '{source}' with index '{index}'")

        PUBMED_DIR = os.getenv('PUBMED_DIR')
        pubmed_data_part = 'baseline' if source < 1219 else 'updatefiles'
        cache_filename = os.path.join(PUBMED_DIR, pubmed_data_part, f"pubmed24n{source:04}.xml.gz")
        if os.path.exists(cache_filename):
            print(f"Loading data from cache '{cache_filename}'")
            tree = etree.parse(cache_filename)
            root = tree.getroot()
            article_node = root.xpath(f"/PubmedArticleSet/PubmedArticle[{index}]")
            paper_info = PaperInfo(article_node[0])

            return paper_info

        url = f"https://ftp.ncbi.nlm.nih.gov/pubmed/{pubmed_data_part}/pubmed24n{source:04}.xml.gz"
        print(f"Local cache file '{cache_filename}' is missing, which could be downloaded from: {url}")
    else:
        print(f"Not found in PubMedIndex: {identifier}")

    paper_info_old, raw_dict = get_paper_info(identifier)
    paper_info = convert_paper_info(paper_info_old, raw_dict)
    return paper_info

def convert_paper_info(old_paper_info, raw_dict):
    paper_info = PaperInfo()
    paper_info._title = old_paper_info.get('title')
    paper_info._journal = old_paper_info.get('journal')
    paper_info._pub_date = old_paper_info.get('pub_date')
    paper_info._pub_year = old_paper_info.get('pub_year')
    paper_info._doi = old_paper_info.get('id', {}).get('doi')
    paper_info._pmid = old_paper_info.get('id', {}).get('pmid')
    paper_info._arxiv_id = old_paper_info.get('id', {}).get('arxiv_id')
    paper_info._pmcid = old_paper_info.get('id', {}).get('pmcid')
    paper_info._cnki_id = old_paper_info.get('id', {}).get('cnki_id')
    #paper_info._issue = old_paper_info.issue
    #paper_info._volume = old_paper_info.volume
    #paper_info._page = old_paper_info.page
    paper_info._authors = old_paper_info.get('authors', [])
    paper_info._affiliations = old_paper_info.get('affiliations', [])
    paper_info._abstract = old_paper_info.get('abstract')
    paper_info._keywords = old_paper_info.get('keywords', [])
    paper_info._language = old_paper_info.get('language')
    return paper_info

def get_paper_info(identifier):
    print('get_paper_info:', identifier)
    identifier_type, id = guess_identifier_type(identifier)
    if identifier_type == "doi":
        return get_paper_info_by_doi(id)
    elif identifier_type == "arxiv_id":
        return get_paper_info_by_arxiv_id(id)
    elif identifier.isdigit():
        return get_paper_info_by_pmid(id)
    elif identifier.startswith("PMC"):
        return get_paper_info_by_pmcid(id)
    else:
        return None, f"Invalid paper ID '{identifier}'"

def get_this_week_start_time():
    today = datetime.today().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
    start_time = today - timedelta(days=7)
    return start_time

def get_stat_all(reviews, group_name, top_n = None):
    stat_all = reviews\
        .values('creator__nickname', 'creator__pk')\
        .annotate(Count('creator'))\
        .order_by('-creator__count')

    if top_n is None:
        top_n = stat_all.count()
        title = '总排名（完整榜单）'
    else:
        title = '总排名（Top10）'

    stat = {
        'name': 'all',
        'title': title,
        'total_count': stat_all.count(),
        'columns': ['排名', '分享者', '分享数'],
        'content': [{
            'id': item['creator__pk'],
            'name': item['creator__nickname'],
            'count': item['creator__count']
        } for item in stat_all[:top_n]],
    }
    if stat_all.count() > top_n:
        stat['full_rank'] = reverse('group:stat_all', kwargs={'group_name':group_name})

    return stat

def get_this_month():
    today = datetime.today().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
    return today.year, today.month

def get_last_month(year, month):
    if month > 1:
        month = month - 1
    else:
        year = year - 1
        month = 12
    return year, month

def get_next_month(year, month):
    if month < 12:
        month = month + 1
    else:
        year = year + 1
        month = 1
    return year, month

def get_deadline(year, month):
    m = CustomCheckInInterval.objects.filter(year=year, month=month)
    if m.count() > 0:
        return m[0].deadline
    return datetime(*get_next_month(year, month), 1).astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))

def get_check_in_interval(year, month):
    start_time = get_deadline(*get_last_month(year, month))
    end_time = get_deadline(year, month)
    return start_time, end_time

def get_stat_this_month(reviews, group_name, top_n = None):
    year, month = get_this_month()
    start_time, end_time = get_check_in_interval(year, month)

    stat_this_month = reviews\
        .filter(create_time__gte=start_time, create_time__lt=end_time)\
        .values('creator__nickname', 'creator__pk')\
        .annotate(Count('creator'), min_create_time=Min('create_time'))\
        .order_by('-creator__count', 'min_create_time')

    this_month = str(year) + '/' + str(month)
    if top_n is None:
        top_n = stat_this_month.count()
        title = f'本月排名（{this_month}，完整榜单）'
    else:
        title = f'本月排名（{this_month}，Top10）'

    stat = {
        'name': 'this-month',
        'title': title,
        'total_count': stat_this_month.count(),
        'columns': ['排名', '分享者', '分享数'],
        'content': [{
            'id': item['creator__pk'],
            'name': item['creator__nickname'],
            'count': item['creator__count']
        } for item in stat_this_month[:top_n]],
    }
    if stat_this_month.count() > top_n:
        stat['full_rank'] = reverse('group:stat_this_month', kwargs={'group_name':group_name})

    return stat

def get_stat_last_month(reviews, group_name, top_n = None):
    today = datetime.today().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
    year = today.year
    month = today.month
    year, month = get_last_month(year, month)

    start_time, end_time = get_check_in_interval(year, month)

    stat_last_month = reviews\
        .filter(create_time__gte=start_time, create_time__lt=end_time)\
        .values('creator__nickname', 'creator__pk')\
        .annotate(Count('creator'), min_create_time=Min('create_time'))\
        .order_by('-creator__count', 'min_create_time')

    last_month = str(year) + '/' + str(month)
    if top_n is None:
        top_n = stat_last_month.count()
        title = f'上月排名（{last_month}，完整榜单）'
    else:
        title = f'上月排名（{last_month}，Top10）'

    stat = {
        'name': 'last-month',
        'title': title,
        'total_count': stat_last_month.count(),
        'columns': ['排名', '分享者', '分享数'],
        'content': [{
            'id': item['creator__pk'],
            'name': item['creator__nickname'],
            'count': item['creator__count']
        } for item in stat_last_month[:top_n]],
    }
    if stat_last_month.count() > top_n:
        stat['full_rank'] = reverse('group:stat_last_month', kwargs={'group_name':group_name})

    return stat

def get_stat_journal(reviews, group_name, top_n = None):
    stat_journal = reviews\
        .exclude(paper__journal='')\
        .values('paper__journal')\
        .annotate(Count('paper__journal'), min_create_time=Min('create_time'))\
        .order_by('-paper__journal__count', 'min_create_time')

    if top_n is None:
        top_n = stat_journal.count()
        title = '杂志排名（完整榜单）'
    else:
        title = '杂志排名（Top10）'

    stat = {
        'name': 'journal',
        'title': title,
        'total_count': stat_journal.count(),
        'columns': ['排名', '杂志', '分享数'],
        'content': [{
            'link': reverse('group:journal', kwargs={'group_name':group_name,'journal_name':item['paper__journal']}),
            'name': item['paper__journal'],
            'count': item['paper__journal__count']
        } for item in stat_journal[:top_n]],
    }
    if stat_journal.count() > top_n:
        stat['full_rank'] = reverse('group:stat_journal', kwargs={'group_name':group_name})

    return stat

def find_key_in_dict(dct, target_key):
    """Recursively search for a target_key in the dictionary."""
    if target_key in dct:  # Base case: key is found at the current level
        return dct[target_key]

    for key, value in dct.items():
        if isinstance(value, dict):  # If the value is a dictionary, go deeper
            result = find_key_in_dict(value, target_key)
            if result is not None:
                return result

    return None  # If the key was never found

def get_abstract_by_pmid(pmid):
    cache_filename = os.path.join(settings.BASE_DIR, "cache/pubmed/" + pmid + ".abs.txt")
    print(f'cache filename: {cache_filename}')
    pubmed_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml'
    data = fetch_json(pubmed_url, cache_filename, is_xml=True)
    if data is not None:
        abstract = find_key_in_dict(data, 'AbstractText')
        if abstract is not None:
            txt = ''
            for item in abstract:
                if isinstance(item, dict):
                    if '#text' in item:
                        if '@Label' in item:
                            txt += item['@Label'] + ': '
                        txt += item['#text']
                else:
                    txt += item
            return txt
    return None

def get_abstract_by_doi(doi):
    pubmed_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={doi}&retmode=json'
    response = requests.get(pubmed_url)

    if response.status_code == 200:
        # Parse the PubMed API response
        pubmed_data = response.json()
        print('esearch returned:', pubmed_data)

        # Check if any PubMed records were found
        if 'esearchresult' in pubmed_data and 'idlist' in pubmed_data['esearchresult']:
            pubmed_ids = pubmed_data['esearchresult']['idlist']
            print('pubmed_ids:', pubmed_ids)

            return get_abstract_by_pmid(pubmed_ids[0])

    return None
