import requests
import json
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
