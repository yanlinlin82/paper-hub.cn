import os
import subprocess
import tempfile
import requests
import json
import zoneinfo
from decouple import config
from paperhub import settings
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from view.models import User, Paper
from group.models import Group
from utils.paper import get_paper_info, convert_string_to_datetime
from utils.paper import get_stat_all, get_stat_this_month, get_stat_last_month, get_stat_journal
from utils.paper import get_abstract_by_doi

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

def fetch_rank_list(request):
    try:
        group_name = 'xiangma'
        group = Group.objects.get(name=group_name)
        papers = group.papers.filter(delete_time=None)

        stat_1 = get_stat_this_month(papers, group_name, top_n=10)
        stat_2 = get_stat_last_month(papers, group_name, top_n=10)
        stat_3 = get_stat_all(papers, group_name, top_n=10)
        stat_4 = get_stat_journal(papers, group_name, top_n=10)

        return JsonResponse({
            'success': True,
            'results': [stat_1, stat_2, stat_3, stat_4]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def fetch_paper_list(request):
    try:
        group_name = 'xiangma'
        group = Group.objects.get(name=group_name)
        papers = group.papers\
            .filter(delete_time=None)\
            .order_by('-create_time', '-pk')

        return JsonResponse({
            'success': True,
            'results': [{
                'creator': p.creator.nickname,
                'create_time': timezone.localtime(p.create_time, timezone=zoneinfo.ZoneInfo(settings.TIME_ZONE)).strftime("%Y-%m-%d %H:%M"),
                'pub_year': p.pub_year,
                'title': p.title,
                'journal': p.journal,
                'comments': p.comments,
                'doi': p.doi,
                'pmid': p.pmid,
                'arxiv_id': p.arxiv_id,
                'pmcid': p.pmcid,
            } for p in papers[:10]]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def ask_chat_gpt(request, paper_id):
    paper = Paper.objects.get(pk=paper_id)
    if paper is None:
        return JsonResponse({"error": "paper not found."})
    if paper.abstract == "":
        if paper.doi != "":
            abstract = get_abstract_by_doi(paper.doi)
            paper.abstract = abstract
            paper.save()
    else:
        abstract = paper.abstract

    # Write the abstract to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(paper.title + '\n')
        temp_file.write(abstract)
        temp_file_path = temp_file.name
        print('temp_file_path:', temp_file_path)

    # Set the environment variable
    os.environ['ALL_PROXY'] = 'socks5://localhost:1090/'

    python_path = os.path.abspath('openai/venv/bin/python')
    script_path = os.path.abspath('openai/test.py')

    try:
        # Call the other Python script with the temporary file as input
        result = subprocess.run([python_path, script_path, temp_file_path], capture_output=True, text=True)
        print('result:', result)

        # Get the return value from stdout
        answer = result.stdout.strip()
        print('answer:', answer)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {e}"})
    finally:
        # Remove the temporary file
        os.remove(temp_file_path)

    os.environ['ALL_PROXY'] = ''
    data = {"abstract": abstract, "answer": answer}
    return JsonResponse(data)
