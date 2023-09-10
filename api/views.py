from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout

from view.models import User
from view.paper import *

def Test(request, text):
    return JsonResponse({
        'success': True,
        "text": text
    })

def Login(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'POST method required!'
            })

    username = request.POST['username']
    password = request.POST['password']
    if username is not None and password is not None:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
    return JsonResponse({'error':'Login failed!'})

def Logout(request):
    logout(request)
    return JsonResponse({'success': True})

def QueryUser(request, user):
    """
    Return JSON:
    {
        "error": "...", /* empty if succeed */
        "query": "...", /* 查询词 */
        "results": {
            "nickname" : "...", /* 昵称 */
            "name"     : "...", /* 姓名 */
            "weixin_id": "...", /* 微信ID */
            "username" : "...", /* 用户名 */
        }
    }
    """
    u = User.objects.filter(nickname=user)
    if u.count() == 0:
        u = User.objects.filter(name=user)
    if u.count() == 0:
        u = User.objects.filter(weixin_id=user)
    if u.count() == 0:
        u = User.objects.filter(username=user)
    if u.count() == 0:
        return JsonResponse({"error": "user '" + user + "' not found."})
    else:
        return JsonResponse({
            'success': True,
            "query": user,
            "results": {
                "nickname": u[0].nickname,
                "name": u[0].name,
                "weixin_id": u[0].weixin_id,
                "username": u[0].username,
            }})

def QueryPaper(request, id):
    """
    Return JSON:
    {
        "error": "...", /* empty if succeed */
        "query": "...", /* 查询词 */
        "raw": { ... }, /* 访问URL的原始结果 */
        "results": {
            "doi"     : "...", /* DOI，唯一标识，据此可查询到信息 */
            "title"   : "...", /* 文献标题 */
            "journal" : "...", /* 杂志名称 */
            "pub_date": "...", /* 发表日期 */
            "authors" : "...", /* 作者列表，半角逗号或回车隔开 */
            "abstract": "...", /* 摘要 */
            "urls"    : "...", /* 超链接，回车隔开 */
        }
    }
    """
    paper_info, raw_dict = get_paper_info(id)
    if paper_info is None:
        return JsonResponse({
            'success': False,
            "error": raw_dict
            })

    return JsonResponse({
        'success': True,
        "query": id,
        "raw": raw_dict,
        "results": {
            "doi": paper_info.get('doi', ''),
            "pmid": paper_info.get('pmid', ''),
            "arxiv_id": paper_info.get('arxiv_id', ''),
            "pmc_id": paper_info.get('pmc_id', ''),
            "title": paper_info.get('title', ''),
            "journal": paper_info.get('journal', ''),
            "pub_date": paper_info.get('pub_date', ''),
            "authors": paper_info.get('authors', ''),
            "abstract": paper_info.get('abstract', ''),
            "urls": paper_info.get('urls', ''),
        }})
