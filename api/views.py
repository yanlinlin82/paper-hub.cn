import os
import requests
import json
import zoneinfo
from paperhub import settings
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from view.models import UserProfile, UserAlias, UserSession, Paper, GroupProfile
from api.paper import get_paper_info, convert_string_to_datetime
from api.paper import get_stat_all, get_stat_this_month, get_stat_last_month, get_stat_journal
from api.paper import get_abstract_by_doi
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.middleware.csrf import get_token
import openai
import httpx
from urllib.parse import quote
import random
import string
from django.db.models import Q
from django.contrib.auth.models import User
import datetime

def parse_request(request):
    if request.content_type != 'application/json':
        return None, JsonResponse({'error': 'Invalid content type'}, status=400)
    try:
        json_data = json.loads(request.body.decode('utf-8'))
        return json_data, None
    except json.JSONDecodeError:
        pass
    return None, JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
def wx_login(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    wx_code = json_data.get('code', '')
    if not wx_code:
        return JsonResponse({'error': 'Invalid wx_code'}, status=400)

    APP_ID = os.getenv('WX_APP_ID')
    SECRET = os.getenv('WX_SECRET')
    if not APP_ID or not SECRET:
        return JsonResponse({'error': 'Invalid APP_ID or SECRET'}, status=400)

    url = 'https://api.weixin.qq.com/sns/jscode2session'\
        f'?appid={APP_ID}&secret={SECRET}&js_code={wx_code}'\
        '&grant_type=authorization_code'
    response = requests.get(url)
    if response.status_code != 200:
        return JsonResponse({'success': False, 'error': 'Login failed! res: ' + response.text})
    if response.json().get('errcode', 0) != 0:
        return JsonResponse({'success': False, 'error': 'Login failed! res: ' + response.text})
    session_key = response.json().get('session_key', '')
    unionid = response.json().get('unionid', '')
    if session_key == '' or unionid == '':
        return JsonResponse({'success': False, 'error': 'Login failed! res: ' + response.text})

    nickname = ''
    users = UserProfile.objects.filter(wx_unionid=unionid)
    if users.count() == 0:
        user = UserProfile(wx_unionid=unionid)
        user.save()
    else:
        user = users[0]
        nickname = user.nickname

    UserSession.objects.filter(user=user, client_type='weixin').delete()
    session = UserSession(user=user, session_key=session_key, client_type='weixin')
    session.save()

    return JsonResponse({
        'success': True,
        'nickname': nickname,
        'csrfToken': get_token(request),
        'token': str(session.token),
        'debug': user.debug_mode
    })

def is_token_valid(token):
    try:
        session = UserSession.objects.get(token=token)
        if timezone.now() > session.expires_at:
            return False
        return True
    except UserSession.DoesNotExist:
        return False

def update_nickname(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    nickname = json_data.get('nickname')
    if not nickname:
        return JsonResponse({'error': 'Nickname is required'}, status=400)
    
    try:
        session = UserSession.objects.get(token=token)
        user = session.user
        user.nickname = nickname
        user.save()
    except UserSession.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid token!'})

    return JsonResponse({'success': True})

def do_login(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    username = json_data.get('username')
    password = json_data.get('password')
    if username is None or password is None:
        return JsonResponse({'error': 'Invalid username or password'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({
            'success': False,
            'error': 'Login failed. Please check your credentials.'
            })

    UserSession.objects.filter(user=user.custom_user, client_type='website').delete()
    session = UserSession(user=user.custom_user, client_type='website')
    session.save()

    login(request, user)
    return JsonResponse({
        'success': True,
        'nickname': user.custom_user.nickname,
        'csrfToken': get_token(request),
        'token': str(session.token),
        'debug': user.custom_user.debug_mode
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
    u = UserProfile.objects.filter(nickname=user)
    if u.count() == 0:
        u = UserProfile.objects.filter(auth_user__username=user)
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
        if UserProfile.objects.filter(nickname=s).count() > 0:
            user = UserProfile.objects.filter(nickname=s)[0]
        elif UserProfile.objects.filter(auth_user__username=s).count() > 0:
            user = UserProfile.objects.filter(auth_user__username=s)[0]
        else:
            user = UserProfile(nickname=s)
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
            group = GroupProfile.objects.get(name=group_name)
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

def fetch_rank_full_list(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    try:
        group_name = json_data.get('group_name')
        group = GroupProfile.objects.get(name=group_name)
        if group is None:
            return JsonResponse({
                'success': False,
                'error': f"Group not found: {group_name}"
            })

        papers = group.papers.filter(delete_time=None)

        index = json_data.get('index', 0)
        if index == 0:
            stat = get_stat_this_month(papers, group_name)
        elif index == 1:
            stat = get_stat_last_month(papers, group_name)
        elif index == 2:
            stat = get_stat_all(papers, group_name)
        elif index == 3:
            stat = get_stat_journal(papers, group_name)
        else:
            return JsonResponse({
                'success': False,
                'error': f"Invalid index: {index}"
            })

        return JsonResponse({
            'success': True,
            'results': stat
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def fetch_rank_list(request):
    print('fetch_rank_list', request)
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    try:
        group_name = json_data.get('group_name')
        group = GroupProfile.objects.get(name=group_name)
        if group is None:
            return JsonResponse({
                'success': False,
                'error': f"Group not found: {group_name}"
            })

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

def get_user_aliases(user):
    aliases = [user]
    for alias in UserAlias.objects.filter(user=user):
        aliases.append(alias.alias)
    for alias in UserAlias.objects.filter(alias=user):
        aliases.append(alias.user)
    return aliases

def fetch_paper_list(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    try:
        group_name = json_data.get('group_name')
        group = GroupProfile.objects.get(name=group_name)
        if group is None:
            return JsonResponse({
                'success': False,
                'error': f"Group not found: {group_name}"
            })

        papers = group.papers.filter(delete_time=None)
        
        mode = json_data.get('mode', 0)
        if mode == 0: # all
            pass
        elif mode == 1: # this month
            papers = papers.filter(create_time__year=timezone.now().year, create_time__month=timezone.now().month)
        elif mode == 2: # last month
            year = timezone.now().year
            month = timezone.now().month
            if month == 1:
                year -= 1
                month = 12
            else:
                month -= 1
            papers = papers.filter(create_time__year=year, create_time__month=month)
        elif mode == 3: # user own
            token = json_data.get('token')
            user = UserSession.objects.get(token=token).user
            aliases = get_user_aliases(user)
            papers = papers.filter(creator__in=aliases)
        else:
            return JsonResponse({
                'success': False,
                'error': f"Invalid mode: {mode}"
            })

        papers = papers.order_by('-create_time', '-pk')

        index = json_data.get('index', 0)
        end_index = index + 10
        return JsonResponse({
            'success': True,
            'results': [{
                'id': p.pk,
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
            } for p in papers[index:end_index]]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def fetch_paper_info(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    paper_id = json_data.get('paper_id')
    paper_info, raw_dict = get_paper_info(paper_id)
    if paper_info is None:
        return JsonResponse({
            'success': False,
            "error": raw_dict
            })

    return JsonResponse({
        'success': True,
        "results": {
            "title": paper_info.get('title', ''),
            "journal": paper_info.get('journal', ''),
            "pub_year": paper_info.get('pub_year', ''),
        }})

def submit_comment(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    try:
        group_name = json_data.get('group_name')
        group = GroupProfile.objects.get(name=group_name)
        if group is None:
            return JsonResponse({
                'success': False,
                'error': f"Group not found: {group_name}"
            })

        paper_id = json_data.get('paper_id')
        title = json_data.get('title')
        pub_year = json_data.get('pub_year')
        journal = json_data.get('journal')
        nickname = json_data.get('nickname')
        comments = json_data.get('comment')

        paper_info, raw_dict = get_paper_info(paper_id)

        user = UserSession.objects.get(token=token).user
        if user.nickname != nickname:
            user.nickname = nickname
            user.save()

        now = timezone.now()
        paper = Paper(creator=user,
                      create_time=now,
                      update_time=now,
                      title=title or paper_info['title'],
                      pub_year=pub_year or paper_info['pub_year'],
                      journal=journal or paper_info['journal'],
                      comments=comments)
        if paper_info is not None:
            paper.doi = paper_info['id'].get('doi', '')
            paper.pmid = paper_info['id'].get('pmid', '')
            paper.arxiv_id = paper_info['id'].get('arxiv_id', '')
            paper.pmcid = paper_info['id'].get('pmcid', '')
            paper.cnki_id = paper_info['id'].get('cnki_id', '')
            paper.authors = "\n".join(paper_info.get('authors', []))
            paper.abstract = paper_info.get('abstract', '')
            paper.urls = "\n".join(paper_info.get('urls', []))

        paper.save()

        group.papers.add(paper)
        group.save()

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def summarize_by_gpt(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    print('token:', token)
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    try:
        group_name = json_data.get('group_name')
        group = GroupProfile.objects.get(name=group_name)
        if group is None:
            return JsonResponse({
                'success': False,
                'error': f"Group not found: {group_name}"
            })

        paper_id = json_data.get('paper_id')
        print('paper_id:', paper_id)
        paper, raw_dict = get_paper_info(paper_id)
        print('paper:', paper)
        if paper is None:
            return JsonResponse({"error": "paper not found."})
        if paper['abstract'] == "":
            paper['abstract'] = get_abstract_by_doi(paper['id']['doi'])

        in_msg = [
            {"role": "system", "content": "This is a scientific paper reading assistance chatbot, using mainly Chinese to chat with user."},
            {"role": "system", "content": "You can ask questions about the paper, or ask for a summary of the paper."},
            {"role": "user", "content": f"Please summarize and comment on the following paper in Chinese:\n\nTitle: {paper['title']}\n\nAbstract:\n{paper['abstract']}"},
        ]
        print('in_msg:', in_msg)
        proxy_url = os.environ.get("OPENAI_PROXY_URL")
        if proxy_url is None or proxy_url == "":
            client = openai.OpenAI()
        else:
            client = openai.OpenAI(http_client=httpx.Client(proxy=proxy_url))
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=in_msg,
        )
        out_msg = completion.choices[0].message.content
        print('out_msg:', out_msg)
        return JsonResponse({'answer': out_msg})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def get_weixin_qr(request):
    appid = os.getenv('WEB_APP_ID')
    web_domain = os.getenv('WEB_DOMAIN')
    redirect_uri = quote(f'https://{web_domain}/api/weixin_callback/')
    current_url = request.GET.get('current_url', f'https://{web_domain}/')
    state = quote(current_url)
    url = f"https://open.weixin.qq.com/connect/qrconnect?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_login&state={state}#wechat_redirect"
    print('get_weixin_qr:', url)
    return JsonResponse({'url': url})

def weixin_callback(request):
    code = request.GET.get('code')
    appid = os.getenv('WEB_APP_ID')
    secret = os.getenv('WEB_APP_SECRET')
    token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code"
    response = requests.get(token_url)
    data = response.json()
    print('weixin_callback:', data)
    access_token = data.get('access_token')
    #expires_in = data.get('expires_in')
    openid = data.get('openid')
    #refresh_token = data.get('refresh_token')
    #scope = data.get('scope')
    unionid = data.get('unionid')
    if openid is None or unionid is None:
        return JsonResponse({'error': 'Invalid openid or unionid'}, status=400)
    
    userinfo_url = f"https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}"
    response2 = requests.get(userinfo_url)
    print('=============', datetime.datetime.now())
    print('response2.content:', response2.content)
    print('response2.text:', response2.text)
    print('response2.headers:', response2.headers)
    nickname = str.encode(response2.json()['nickname'], 'latin1').decode('utf8')
    print('nickname:', nickname)
    
    profiles = UserProfile.objects.filter(
        Q(wx_unionid=unionid) | Q(wx_openid=openid)
    )
    if profiles.count() == 0:
        def generate_random_username():
            letters = string.ascii_letters
            return 'u-' + ''.join(random.choice(letters) for _ in range(10))
        def get_unique_random_username():
            while True:
                username = generate_random_username()
                if User.objects.filter(username=username).count() == 0:
                    return username
        username = get_unique_random_username()      
        user = User(username=username)
        user.save()
        profile = UserProfile(auth_user=user, nickname=nickname, wx_openid=openid, wx_unionid=unionid)
        profile.save()
    else:
        profile = profiles[0]
        user = profile.auth_user
        if profile.nickname != nickname:
            profile.nickname = nickname
            profile.save()
        if profile.wx_openid != openid or profile.wx_unionid != unionid:
            profile.wx_openid = openid
            profile.wx_unionid = unionid
            profile.save()

    UserSession.objects.filter(user=profile, client_type='website').delete()
    session = UserSession(user=profile, session_key='', client_type='website')
    session.save()

    login(request, user)
    redirect_to = request.GET.get('state')
    return HttpResponseRedirect(redirect_to)
