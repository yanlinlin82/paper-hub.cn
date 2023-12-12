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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from group.models import CustomCheckInInterval
from paperhub import settings
import requests

def convert_string_to_datetime(s):
    format_strings = ['%Y-%m-%d', '%m/%d/%Y',
                      '%d-%b-%Y', '%Y %b %d', '%b %d, %Y', '%d %b, %Y',
                      '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%SZ',
                      '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']
    for format_string in format_strings:
        try:
            dt = datetime.strptime(s, format_string)
            return dt
        except ValueError:
            pass  # continue to the next format string
    return None

def extract_year_from_dict(data, key):
    if key not in data:
        return None
    dt = convert_string_to_datetime(data[key])
    if dt is None:
        return None
    return dt.year

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
    text_data = fetch_and_cache(api_url, cache_filename)
    if text_data is None:
        return None

    if is_xml:
        xml_dict = xmltodict.parse(text_data)
        text_data = json.dumps(xml_dict)

    try:
        json_data = json.loads(text_data)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        return None

# Function to query paper info by arXiv ID
def get_paper_info_by_arxiv_id(arxiv_id):
    cache_filename = os.path.join(settings.BASE_DIR, "cache/arxiv/" + arxiv_id + ".txt")
    api_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    data = fetch_json(api_url, cache_filename, is_xml=True)
    if 'feed' in data and 'entry' in data['feed']:
        obj = data['feed']['entry']
        paper_info = {
            'id': {
                'doi': f"10.48550/arXiv.{arxiv_id}",
                'arxiv_id': arxiv_id,
            },
            'title': obj.get('title', ''),
            'journal': 'arXiv',
            'abstract': obj.get('summary', ''),
            'pub_year': extract_year_from_dict(obj, 'published'),
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

        paper_info = {
            'id': {'pmid': pmid},
            'title': obj.get('title', ''),
            'journal': obj.get('fulljournalname', ''),
            'pub_year': extract_year_from_dict(obj, 'pubdate'),
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
        type = obj.get('type', '')
        title = " ".join(obj.get('title', []))
        journal = " ".join(obj.get('container-title', []))
        if 'created' in obj:
            pub_year = extract_year_from_dict(obj['created'], 'date-time')
        issue = obj.get('issue', '')
        volume = obj.get('volume', '')
        page = obj.get('page', '')
        abstract = obj.get('abstract', '')

        paper_info = {
            'id': {'doi': doi},
            'type': type,
            'title': title,
            'journal': journal,
            'pub_year': pub_year,
            'issue': issue,
            'volume': volume,
            'page': page,
            'abstract': abstract,
            'authors': [node.get('given', '') + ' ' + node.get('family', '') for node in obj.get('author', [])],
            'urls': list(dict.fromkeys([node["URL"] for node in obj.get('link', [])]))
        }
        return paper_info, data
    return None, f"Query DOI '{doi}' failed!"

def get_paper_info(identifier):
    if identifier.startswith("10."):
        # DOI
        doi = identifier
        pattern_arxiv = re.compile('^10\.48550\/arXiv\.([0-9]+\.[0-9]+)$')
        m = pattern_arxiv.match(doi)
        if m:
            # arXiv ID
            arxiv_id = m.group(1)
            return get_paper_info_by_arxiv_id(arxiv_id)
        return get_paper_info_by_doi(doi)
    elif re.match(r'^(arXiv:)?\d{4}\.\d{5}$', identifier):
        # arXiv ID
        arxiv_id = identifier.replace("arXiv:", "")
        return get_paper_info_by_arxiv_id(arxiv_id)
    elif identifier.isdigit():
        # Check if it's a number (PMID)
        pmid = identifier
        return get_paper_info_by_pmid(pmid)
    elif identifier.startswith("PMC"):
        # PMC ID
        pmcid = identifier
        return get_paper_info_by_pmcid(pmcid)
    else:
        # invalid ID
        return None, f"Invalid paper ID '{identifier}'"

def main() -> int:
    if len(sys.argv) < 2:
        print(f"""
Usage: python {sys.argv[0]} <doi/pmid/pmcid/arxivid>

For example:
  1. DOI: 10.1101/2023.09.06.556610
  2. PMID: 37683932, 37678251
  3. PMCID: PMC9478175
  4. arXiv ID: 2306.03301
""")
        return 2
    id = sys.argv[1]

    paper_info, raw = get_paper_info(id)
    if paper_info is None:
        print(f"ERROR: Failed to get paper info by {id}", file=sys.stderr)
        return 1

    print(json.dumps(paper_info))
    return 0

def get_this_week_start_time():
    today = datetime.today().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
    start_time = today - timedelta(days=7)
    return start_time

def get_paginated_papers(papers, page_number):
    if page_number is None:
        page_number = 1

    p = Paginator(papers, 20)
    try:
        papers = p.get_page(page_number)
    except PageNotAnInteger:
        page_number = 1
        papers = p.page(1)
    except EmptyPage:
        page_number = p.num_pages
        papers = p.page(p.num_pages)

    items = list(papers)
    indices = list(range((papers.number - 1) * p.per_page + 1, papers.number * p.per_page + 1))

    return papers, zip(items, indices)

def filter_papers(papers, page_number, id=None, user=None, trash=False, journal_name=None, start_time=None, end_time=None):
    if id is not None:
        papers = papers.filter(pk=id)

    if user is not None:
        papers = papers.filter(creator=user)

    if trash:
        papers = papers.exclude(delete_time=None)
    else:
        papers = papers.filter(delete_time=None)

    if journal_name is not None:
        papers = papers.filter(journal=journal_name)

    if start_time is not None:
        papers = papers.filter(create_time__gte=start_time)
    if end_time is not None:
        papers = papers.filter(create_time__lt=end_time)

    papers = papers.order_by('-create_time', '-pk')
    return get_paginated_papers(papers, page_number)

def get_stat_all(papers, group_name, top_n = None):
    stat_all = papers\
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

def get_stat_this_month(papers, group_name, top_n = None):
    year, month = get_this_month()
    start_time, end_time = get_check_in_interval(year, month)

    stat_this_month = papers\
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

def get_stat_last_month(papers, group_name, top_n = None):
    today = datetime.today().astimezone(zoneinfo.ZoneInfo(settings.TIME_ZONE))
    year = today.year
    month = today.month
    year, month = get_last_month(year, month)

    start_time, end_time = get_check_in_interval(year, month)

    stat_last_month = papers\
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

def get_stat_journal(papers, group_name, top_n = None):
    stat_journal = papers\
        .exclude(journal='')\
        .values('journal')\
        .annotate(Count('journal'), min_create_time=Min('create_time'))\
        .order_by('-journal__count', 'min_create_time')

    if top_n is None:
        top_n = stat_journal.count()
        title = '杂志排名（完整榜单）'
    else:
        title = '杂志排名（Top10）'

    stat = {
        'name': 'journal',
        'title': title,
        'columns': ['排名', '杂志', '分享数'],
        'content': [{
            'link': reverse('group:journal', kwargs={'group_name':group_name,'journal_name':item['journal']}),
            'name': item['journal'],
            'count': item['journal__count']
        } for item in stat_journal[:top_n]],
    }
    if stat_journal.count() > top_n:
        stat['full_rank'] = reverse('group:stat_journal', kwargs={'group_name':group_name})

    return stat

def get_abstract_by_pmid(pmid):
    pubmed_url = f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml'
    response = requests.get(pubmed_url)

    if response.status_code == 200:
        # Parse the PubMed XML response
        xml_data = response.text
        abstract_start = xml_data.find('<AbstractText>') + len('<AbstractText>')
        abstract_end = xml_data.find('</AbstractText>')
        abstract = xml_data[abstract_start:abstract_end].strip()
        return abstract

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

if __name__ == '__main__':
    sys.exit(main())
