import os
import sys
import requests
import json
import xmltodict
import re
from django.http import JsonResponse
from .models import CrossRefCache
import xml.etree.ElementTree as ET
import numpy as np

def query_pubmed(pmid):
    print('query_pubmed: ', pmid)
    return JsonResponse({"error": "PMID (" + pmid + ") is still not supported"}, status=400)

def query_arxiv(arxiv_id):
    print('query_arxiv: ', arxiv_id)
    cache = CrossRefCache.objects.filter(type=CrossRefCache.arXiv, key=arxiv_id)
    print(cache.count())
    if cache.count() == 0:
        try:
            url = 'http://export.arxiv.org/api/query?id_list=' + arxiv_id
            xml_text = requests.get(url).text
        except:
            return JsonResponse({"error": "Failed to query json from URL: " + url}, status=400)
        item = CrossRefCache(type=CrossRefCache.arXiv, key=arxiv_id, value=xml_text)
        item.save()
    else:
        xml_text = cache[0].value
    print(xml_text)
    xml = ET.fromstring(xml_text)

    return JsonResponse({"error": "arXiv (" + arxiv_id + ") is still not supported"}, status=400)

def query_doi(doi):
    print('query_doi: ', doi)
    cache = CrossRefCache.objects.filter(type=CrossRefCache.DOI, key=doi)
    if cache.count() == 0:
        try:
            url = 'http://api.crossref.org/works/' + doi
            data = requests.get(url).json()
        except:
            return JsonResponse({"error": "Failed to query json from URL: " + url}, status=400)
        item = CrossRefCache(type=CrossRefCache.DOI, key=doi, value=json.dumps(data))
        item.save()
    else:
        data = json.loads(cache[0].value)

    try:
        type = data["message"]["type"]
    except:
        type = ""

    try:
        title = " ".join(data["message"]["title"])
    except:
        title = ""
    
    try:
        journal = " ".join(data["message"]["container-title"])
    except:
        journal = ""

    try:
        pub_date = data["message"]["created"]["date-time"][0:10]
    except:
        pub_date = ""
    
    try:
        issue = data["message"]["issue"]
    except:
        issue = ""

    try:
        volume = data["message"]["volume"]
    except:
        volume = ""

    try:
        page = data["message"]["page"]
    except:
        page = ""

    try:
        abstract = data["message"]["abstract"]
    except:
        abstract = ""

    try:
        authors = "\n".join(node["given"] + " " + node["family"] for node in data["message"]["author"])
    except:
        authors = ""

    try:
        links = [node["URL"] for node in data["message"]["link"]]
        urls = "\n".join(list(np.unique(links)))
    except:
        urls = ""

    return JsonResponse({"error": "", "doi": doi, "results": {
        "doi": doi,
        "type": type,
        "title": title,
        "journal": journal,
        "pub_date": pub_date,
        "issue": issue,
        "volume": volume,
        "page": page,
        "authors": authors,
        "abstract": abstract,
        "urls": urls,
    }}, status=200)

def eprint(*args, **kwargs): # print to stderr instead of stdout
    print(*args, file=sys.stderr, **kwargs)

def fetch_and_cache(url, cache_filename):
    if os.path.exists(cache_filename):
        # If the cache file exists, load the data from it
        with open(cache_filename, 'r', encoding='utf-8') as cache_file:
            data = cache_file.read()
        eprint(f"Loaded data from cache '{cache_filename}'")
    else:
        # If the cache file doesn't exist, fetch data from the URL
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text
            # Cache the data to a local file
            os.makedirs(os.path.dirname(cache_filename), mode=0o755, exist_ok=True)
            with open(cache_filename, 'w', encoding='utf-8') as cache_file:
                cache_file.write(data)
            eprint(f"Fetched data from the URL and cached it: {url}")
        else:
            eprint("Failed to fetch data from the URL.")
            data = None
    return data

def fetch_json(api_url, cache_filename, is_xml=False):
    print(api_url)
    text_data = fetch_and_cache(api_url, cache_filename)

    if is_xml:
        xml_dict = xmltodict.parse(text_data)
        text_data = json.dumps(xml_dict)

    try:
        json_data = json.loads(text_data)
        return json_data
    except json.JSONDecodeError as e:
        eprint(f"Error decoding JSON: {e}")
        return None

# Function to query paper info by arXiv ID
def get_paper_info_by_arxiv_id(arxiv_id):
    cache_filename = "cache/arxiv/" + arxiv_id + ".txt"
    api_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    data = fetch_json(api_url, cache_filename, is_xml=True)
    if 'feed' in data and 'entry' in data['feed']:
        paper_info = data['feed']['entry']
        return paper_info, data
    return None, f"Query arXiv ID '{arxiv_id}' failed!"

# Function to query paper info by PubMed ID (PMID)
def get_paper_info_by_pmid(pmid):
    cache_filename = "cache/pubmed/" + pmid + ".txt"
    api_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    data = fetch_json(api_url, cache_filename)
    if 'result' in data and pmid in data['result']:
        paper_info = data['result'][pmid]
        return paper_info, data
    return None, f"Query PubMed ID '{pmid}' failed!"

# Function to query paper info by PMC ID
def get_paper_info_by_pmc_id(pmc_id):
    cache_filename = "cache/pmc/" + pmc_id + ".txt"
    api_url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids={pmc_id}&format=json"
    data = fetch_json(api_url, cache_filename)
    if 'records' in data and len(data['records']) > 0:
        paper_info = data['records'][0]
        return paper_info, data
    return None, f"Query PMC ID '{pmc_id}' failed!"

# Function to query paper info by DOI
def get_paper_info_by_doi(doi):
    cache_filename = "cache/doi/" + doi + ".txt"
    api_url = f"https://api.crossref.org/works/{doi}"
    data = fetch_json(api_url, cache_filename)
    if 'message' in data:
        obj = data['message']
        type = obj.get('type', '')
        title = " ".join(obj.get('title', []))
        journal = " ".join(obj.get('container-title', []))
        pub_date = obj.get('created', {'date-time':''}).get('date-time', '')[0:10]
        issue = obj.get('issue', '')
        volume = obj.get('volume', '')
        page = obj.get('page', '')
        abstract = obj.get('abstract', '')
        authors = "\n".join(node.get('given', '') + ' ' + node.get('family', '') for node in obj.get('author', []))
        urls = "\n".join(list(np.unique([node["URL"] for node in obj.get('link', [])])))

        paper_info = {
            'doi': doi,
            'type': type,
            'title': title,
            'journal': journal,
            'pub_date': pub_date,
            'issue': issue,
            'volume': volume,
            'page': page,
            'abstract': abstract,
            'authors': authors,
            'urls': urls
        }
        print(paper_info)
        #print(data)
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

    #pattern_pubmed = re.compile('^[0-9]+$')
    #if pattern_pubmed.search(id):
    #    return query_pubmed(id)
    #pattern_arxiv = re.compile('^10\.48550\/arXiv\.([0-9]+\.[0-9]+)$')
    #m = pattern_arxiv.match(id)
    #if m:
    #    arxiv_id = m.group(1)
    #    return query_arxiv(arxiv_id)
    #else:
    #    return query_doi(id)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s <id>" % sys.argv[0])
        exit(1)

    identifier = sys.argv[1]
    paper_info = get_paper_info(identifier)

    if paper_info:
        print("Title:", paper_info.get('title', 'N/A'))
        print("Authors:", ', '.join(paper_info.get('author', ['N/A'])))
        print("Publication Date:", paper_info.get('published', 'N/A'))
        print("Abstract:", paper_info.get('abstract', 'N/A'))
    else:
        print("No information found for the given identifier.")
