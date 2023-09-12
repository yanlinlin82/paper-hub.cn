from django.shortcuts import render, redirect
from django.conf import settings
from utils.paper import get_paper_info

def index(request):
    if settings.CONFIG_XIANGMA_GROUP_ONLY:
        return redirect("group:all", group_name='xiangma')

    context = {}

    query = request.GET.get('q')
    if query is not None:
        context['query'] = query
        paper_info, raw_dict = get_paper_info(query)
        if paper_info is None:
            context['error_message'] = f"Failed to query paper info with '{query}'!"
        else:
            context['results'] = [{
                "id": paper_info.get('id'),
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
