import os
import sys
import requests
import json
import xmltodict
import re
import datetime

def extract_year_from_dict(data, key):
    format_strings = ['%Y-%m-%d', '%m/%d/%Y',
                      '%d-%b-%Y', '%Y %b %d', '%b %d, %Y', '%d %b, %Y',
                      '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%SZ']
    if key in data:
        for format_string in format_strings:
            try:
                date_value = datetime.datetime.strptime(data[key], format_string)
                year = date_value.year
                return year
            except ValueError:
                pass  # continue to the next format string
    return None

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
            os.makedirs(os.path.dirname(cache_filename), mode=0o755, exist_ok=True)
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
    cache_filename = "cache/arxiv/" + arxiv_id + ".txt"
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
    cache_filename = "cache/pubmed/" + pmid + ".txt"
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
def get_paper_info_by_pmc_id(pmc_id):
    cache_filename = "cache/pmc/" + pmc_id + ".txt"
    api_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmc_id}&format=json"
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
        return None, f"Query PMC ID '{pmc_id}' failed!"
    else:
        return paper_info, raw_data

# Function to query paper info by DOI
def get_paper_info_by_doi(doi):
    cache_filename = "cache/doi/" + doi + ".txt"
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
        pmc_id = identifier
        return get_paper_info_by_pmc_id(pmc_id)
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

if __name__ == '__main__':
    sys.exit(main())
