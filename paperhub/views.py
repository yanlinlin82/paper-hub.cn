from django.shortcuts import render
from utils.paper import *

def index(request):
    context = {}

    query = request.GET.get('q')
    if query is not None:
        context['query'] = query
        paper_info, raw_dict = get_paper_info(query)
        if paper_info is None:
            context['error_message'] = f"Failed to query paper info with '{query}'!"
        else:
            context['results'] = [{
                "doi": paper_info.get('doi', ''),
                "pmid": paper_info.get('pmid', ''),
                "arxiv_id": paper_info.get('arxiv_id', ''),
                "pmc_id": paper_info.get('pmc_id', ''),
                "title": paper_info.get('title', ''),
                "journal": paper_info.get('journal', ''),
                "pub_date": paper_info.get('pub_date', ''),
                "authors": paper_info.get('authors', []),
                "abstract": paper_info.get('abstract', ''),
                "urls": paper_info.get('urls', []),
            }]
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')
