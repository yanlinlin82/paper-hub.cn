from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from view.models import User, Paper
from group.models import Group
from utils.paper import get_paper_info, convert_string_to_datetime
import requests
import json
from decouple import config

def wx_login(request):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'POST method required!'
            })

    APPID = config('WX_APPID')
    SECRET = config('WX_SECRET')
    wx_login_code = request['POST'].code

    url = f'https://api.weixin.qq.com/sns/jscode2session'\
        '?appid={APPID}&secret={SECRET}&js_code={wx_login_code}'\
        '&grant_type=authorization_code'
    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse({'error':'Login failed!'})

    res = json.loads(response.text)
    openid = res.data.openid
    session_key = res.data.session_key

    print(f"result: openid={openid}, session_key={session_key}")
    return JsonResponse({'success': True})

def do_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username is not None and password is not None:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True})
    return JsonResponse({
        'success': False,
        'error': 'Login failed. Please check your credentials.'
        })

def do_logout(request):
    logout(request)
    return JsonResponse({'success': True})

def query_user(request, user):
    """
    Return JSON:
    {
        "success": True/False,
        "error": "...", /* empty if succeed */
        "query": "...", /* 查询词 */
        "results": {
            "nickname" : "...", /* 昵称 */
            "username" : "...", /* 用户名 */
        }
    }
    """
    u = User.objects.filter(nickname=user)
    if u.count() == 0:
        u = User.objects.filter(auth_user__username=user)
    if u.count() == 0:
        return JsonResponse({"error": "user '" + user + "' not found."})
    else:
        return JsonResponse({
            'success': True,
            "query": user,
            "results": {
                "nickname": u[0].nickname,
                "username": u[0].auth_user.username,
            }})

def query_paper(request, id):
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
            "pmcid": paper_info.get('pmcid', ''),
            "title": paper_info.get('title', ''),
            "journal": paper_info.get('journal', ''),
            "pub_year": paper_info.get('pub_year', ''),
            "authors": paper_info.get('authors', []),
            "abstract": paper_info.get('abstract', ''),
            "urls": paper_info.get('urls', []),
        }})

def add_paper(request):
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

    try:
        s = request.POST['username']
        if User.objects.filter(nickname=s).count() > 0:
            user = User.objects.get(nickname=s)
        elif User.objects.filter(name=s).count() > 0:
            user = User.objects.get(name=s)
        elif User.objects.filter(weixin_id=s) > 0:
            user = User.objects.get(weixin_id=s)
        elif User.objects.filter(username=s).count() > 0:
            user = User.objects.get(username=s)
        else:
            user = User(username=s, nickname=s)
            user.save()

        if 'create_time' in request.POST:
            s = request.POST['create_time']
            create_time = convert_string_to_datetime(s)
            if create_time is None:
                return JsonResponse({
                    'success': False,
                    'error': f"Invalid format of 'create_time': '{s}'!"
                    })
            create_time = timezone.make_aware(create_time, timezone.get_current_timezone())
        else:
            create_time = timezone.now()

        p = Paper(
            creator = user,
            create_time = create_time,
            update_time = create_time)

        p.title = request.POST['title']
        p.pub_year = request.POST['pub_year']
        p.journal = request.POST['journal']
        p.comments = request.POST['comment']

        paper_id = request.POST['paper_id']
        paper_info, raw_dict = get_paper_info(paper_id)
        if paper_info is not None:
            p.doi = paper_info['id'].get('doi', '')
            p.pmid = paper_info['id'].get('pmid', '')
            p.arxiv_id = paper_info['id'].get('arxiv_id', '')
            p.pmcid = paper_info['id'].get('pmcid', '')
            p.cnki_id = paper_info['id'].get('cnki_id', '')
            p.authors = "\n".join(paper_info.get('authors', []))
            p.abstract = paper_info.get('abstract', '')
            p.urls = "\n".join(paper_info.get('urls', []))
        p.save()

        group_name = request.POST['group_name']
        if group_name:
            group = Group.objects.get(name=group_name)
        group.papers.add(p)
        group.save()

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def edit_paper(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['id']
        #paper_id = request.POST['paper_id']  # TODO: query paper info
        p = Paper.objects.get(pk=id)
        p.title = request.POST['title']
        p.pub_year = request.POST['pub_year']
        p.journal = request.POST['journal']
        p.comments = request.POST['comment']
        p.save()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def delete_paper(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['paper_id']
        p = Paper.objects.get(pk=id)
        p.delete_time = timezone.now()
        p.save()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def restore_paper(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['paper_id']
        p = Paper.objects.get(pk=id)
        p.delete_time = None
        p.save()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def delete_paper_forever(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['paper_id']
        Paper.objects.get(pk=id)
        Paper.objects.filter(pk=id).delete()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})
