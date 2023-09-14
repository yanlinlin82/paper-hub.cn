from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from view.models import User, Paper
from utils.paper import get_paper_info

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
            "pub_year": "...", /* 发表年份 */
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
            "pub_year": paper_info.get('pub_year', ''),
            "authors": paper_info.get('authors', []),
            "abstract": paper_info.get('abstract', ''),
            "urls": paper_info.get('urls', []),
        }})

def EditPaper(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'POST method required!'
            })

    id = request.POST['id']
    papers = Paper.objects.filter(pk=id)
    if papers.count() <= 0:
        return JsonResponse({
            'success': True,
            'error': f'Paper (pk={id}) does not exist!',
        })

    print(request.POST)
    p = papers[0]
    p.title = request.POST['title']
    p.pub_year = request.POST['pub_year']
    p.journal = request.POST['journal']
    p.comments = request.POST['comment']
    p.save()

    return JsonResponse({'success': True})

def DeletePaper(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'POST method required!'
            })

    paper_id = request.POST['paper_id']
    papers = Paper.objects.filter(pk=paper_id)
    if papers.count() <= 0:
        return JsonResponse({
            'success': True,
            'error': f'Paper (pk={paper_id}) does not exist!',
        })

    p = papers[0]
    p.delete_time = timezone.now()
    p.save()
    
    return JsonResponse({'success': True})

def RestorePaper(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'POST method required!'
            })

    paper_id = request.POST['paper_id']
    papers = Paper.objects.filter(pk=paper_id)
    if papers.count() <= 0:
        return JsonResponse({
            'success': True,
            'error': f'Paper (pk={paper_id}) does not exist!',
        })

    p = papers[0]
    p.delete_time = None
    p.save()
    
    return JsonResponse({'success': True})

def DeletePaperForever(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'POST method required!'
            })

    paper_id = request.POST['paper_id']
    papers = Paper.objects.filter(pk=paper_id)
    if papers.count() <= 0:
        return JsonResponse({
            'success': True,
            'error': f'Paper (pk={paper_id}) does not exist!',
        })

    Paper.objects.filter(pk=paper_id).delete()
    
    return JsonResponse({'success': True})
