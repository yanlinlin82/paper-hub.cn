from django.http import JsonResponse
from django.shortcuts import render

from view.models import Paper, User
from view.paper import *

def QueryUser(request, user):
    u = User.objects.filter(nickname=user)
    if u.count() == 0:
        u = User.objects.filter(name=user)
    if u.count() == 0:
        u = User.objects.filter(weixin_id=user)
    if u.count() == 0:
        u = User.objects.filter(username=user)
    if u.count() == 0:
        return JsonResponse({"error": "user '" + user + "' not found."}, status=200)
    else:
        return JsonResponse({"error": "", "query": user, "results": {
            "nickname": u[0].nickname,
            "name": u[0].name,
            "weixin_id": u[0].weixin_id,
            "username": u[0].username,
        }}, status=200)

def QueryPaper(request, id):
    pattern_pubmed = re.compile('^[0-9]+$')
    if pattern_pubmed.search(id):
        return query_pubmed(id)
    pattern_arxiv = re.compile('^10\.48550\/arXiv\.([0-9]+\.[0-9]+)$')
    m = pattern_arxiv.match(id)
    if m:
        arxiv_id = m.group(1)
        return query_arxiv(arxiv_id)
    else:
        return query_doi(id)
