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
from view.models import CustomCheckInInterval
from paperhub import settings
import requests

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
            'title': obj.get('title', ''),
            'journal': 'arXiv',
            'abstract': obj.get('summary', ''),
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
            'title': obj.get('title', ''),
            'journal': obj.get('fulljournalname', ''),
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
        type = obj.get('type', '')
        title = " ".join(obj.get('title', []))
        journal = " ".join(obj.get('container-title', []))
        if 'created' in obj:
            pub_date, pub_year = extract_date_and_year_from_dict(obj['created'], 'date-time')
        issue = obj.get('issue', '')
        volume = obj.get('volume', '')
        page = obj.get('page', '')
        abstract = obj.get('abstract', '')

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
            'authors': [node.get('given', '') + ' ' + node.get('family', '') for node in obj.get('author', [])],
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

def get_paginated_reviews(reviews, page_number):
    if page_number is None:
        page_number = 1

    p = Paginator(reviews, 20)
    try:
        reviews = p.get_page(page_number)
    except PageNotAnInteger:
        page_number = 1
        reviews = p.page(1)
    except EmptyPage:
        page_number = p.num_pages
        reviews = p.page(p.num_pages)

    items = list(reviews)
    indices = list(range((reviews.number - 1) * p.per_page + 1, reviews.number * p.per_page + 1))

    return reviews, zip(items, indices)

def filter_reviews(reviews, page_number, id=None, user=None, trash=False, journal_name=None, start_time=None, end_time=None):
    if id is not None:
        reviews = reviews.filter(pk=id)

    if user is not None:
        reviews = reviews.filter(creator=user)

    if trash:
        reviews = reviews.exclude(delete_time=None)
    else:
        reviews = reviews.filter(delete_time=None)

    if journal_name is not None:
        reviews = reviews.filter(journal=journal_name)

    if start_time is not None:
        reviews = reviews.filter(create_time__gte=start_time)
    if end_time is not None:
        reviews = reviews.filter(create_time__lt=end_time)

    reviews = reviews.order_by('-create_time', '-pk')
    return get_paginated_reviews(reviews, page_number)

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

if __name__ == '__main__':
    sys.exit(main())
