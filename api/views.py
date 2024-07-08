import os
import requests
import json
import zoneinfo
import httpx
import random
import string
import datetime
import uuid
from urllib.parse import quote
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.middleware.csrf import get_token
from django.db.models import Q
from django.contrib.auth.models import User
import openai
from paperhub import settings
from view.models import UserProfile, UserAlias, UserSession, Review, GroupProfile, Recommendation, Paper, PaperTranslation
from api.paper import guess_identifier_type, get_paper_info_new, get_paper_info, convert_string_to_datetime
from api.paper import get_stat_all, get_stat_this_month, get_stat_last_month, get_stat_journal
from api.paper import get_abstract_by_doi

from functools import wraps

def json_view(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
        try:
            data = json.loads(request.body)
            request.json_data = data
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return wrapper

def require_login(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
        return func(request, *args, **kwargs)
    return wrapper

def parse_request(request):
    print('parse_request:', request)
    print(f'request.content_type = {request.content_type}')
    if request.content_type != 'application/json':
        return None, JsonResponse({'error': 'Invalid content type'}, status=400)
    try:
        print(f'parse_request: {request.body}')
        json_data = json.loads(request.body.decode('utf-8'))
        print(f'parse_request: {json_data}')
        return json_data, None
    except json.JSONDecodeError:
        print(f'parse_request: Invalid JSON')
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

@json_view
def do_login(request):
    data = request.json_data
    username = data.get('username')
    password = data.get('password')
    if username is None or password is None:
        return JsonResponse({'success': False, 'error': 'Invalid username or password'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'success': False, 'error': 'Login failed. Please check your credentials.'})

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

def query_review(request, id):
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
    review_info, raw_dict = get_paper_info(id)
    if review_info is None:
        return JsonResponse({
            'success': False,
            "error": raw_dict
            })

    return JsonResponse({
        'success': True,
        "query": id,
        "raw": raw_dict,
        "results": {
            "doi": review_info.get('doi', ''),
            "pmid": review_info.get('pmid', ''),
            "arxiv_id": review_info.get('arxiv_id', ''),
            "pmcid": review_info.get('pmcid', ''),
            "title": review_info.get('title', ''),
            "journal": review_info.get('journal', ''),
            "pub_year": review_info.get('pub_year', ''),
            "authors": review_info.get('authors', []),
            "abstract": review_info.get('abstract', ''),
            "urls": review_info.get('urls', []),
        }})

def query_paper_info(request):
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
        identifier = request.POST['identifier']
        print(f'query_paper_info: {identifier}')

        identifier_type, identifier = guess_identifier_type(identifier)
        print(f'  identifier_type: {identifier_type}')
        if identifier_type == "pmid" or identifier_type == "doi":
            paper_info = get_paper_info_new(identifier, identifier_type)
        else:
            paper_info, raw_dict = get_paper_info(identifier)

        return JsonResponse({
            'success': True,
            'results': {
                'identifier': identifier,
                'identifier_type': identifier_type,
                'title': paper_info.title,
                'journal': paper_info.journal,
                'pub_date': paper_info.pub_date,
                'pub_year': paper_info.pub_year,
                'authors': paper_info.authors,
                'affiliations': paper_info.affiliations,
                'abstract': paper_info.abstract,
                'keywords': paper_info.keywords,
                'urls': paper_info.urls,
                'doi': paper_info.doi,
                'pmid': paper_info.pmid,
                'arxiv_id': paper_info.arxiv_id,
                'pmcid': paper_info.pmcid,
                'cnki_id': paper_info.cnki_id,
                'language': paper_info.language,
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def submit_review(request):
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
        print(f'submit_review: {request.POST}')

        review_id = int(request.POST['review_id'])
        paper_id = int(request.POST['paper_id'])
        comment = request.POST['comment']

        review = Review.objects.get(pk=review_id)
        if review is None:
            return JsonResponse({
                'success': False,
                'error': f"Review not found: {review_id}"
            })
        if review.paper.pk != paper_id:
            return JsonResponse({
                'success': False,
                'error': f"Review {review_id} does not match paper {paper_id} (expected {review.paper.pk})"
            })
        if not request.user.is_superuser and review.creator != request.user.custom_user:
            return JsonResponse({
                'success': False,
                'error': f"Review {review_id} is not created by user {request.user.custom_user} (expected {review.creator})"
            })

        if review.comment != comment:
            review.comment = comment
            review.save()
        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def add_review(request):
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

        paper = Paper(
            journal = request.POST['journal'],
            pub_year = request.POST['pub_year'],
            title = request.POST['title']
        )
        review_id = request.POST['review_id']
        paper_info, raw_dict = get_paper_info(review_id)
        if paper_info is not None:
            paper.doi = paper_info.get('doi', '')
            paper.pmid = paper_info.get('pmid', '')
            paper.arxiv_id = paper_info.get('arxiv_id', '')
            paper.pmcid = paper_info.get('pmcid', '')
            paper.authors = "\n".join(paper_info.get('authors', []))
            paper.abstract = paper_info.get('abstract', '')
            paper.urls = "\n".join(paper_info.get('urls', []))
        paper.save()

        review = Review(
            paper = paper,
            creator = user,
            create_time = create_time,
            update_time = create_time,
            comment = request.POST['comment'])
        review.save()

        group_name = request.POST['group_name']
        if group_name:
            group = GroupProfile.objects.get(name=group_name)
            group.reviews.add(review)
            group.save()

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def edit_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['id']
        #review_id = request.POST['review_id']  # TODO: query review info
        p = Review.objects.get(pk=id)
        p.title = request.POST['title']
        p.pub_year = request.POST['pub_year']
        p.journal = request.POST['journal']
        p.comment = request.POST['comment']
        p.save()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def delete_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['review_id']
        p = Review.objects.get(pk=id)
        p.delete_time = timezone.now()
        p.save()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def restore_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['review_id']
        p = Review.objects.get(pk=id)
        p.delete_time = None
        p.save()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def delete_review_forever(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        id = request.POST['review_id']
        Review.objects.get(pk=id)
        Review.objects.filter(pk=id).delete()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

    return JsonResponse({'success': True})

def add_search_result(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'User is not authenticated!',
        })

    try:
        paper_id = request.POST['paper_id']
        comment = request.POST['comment']

        user = request.user.custom_user

        paper = Paper.objects.get(pk=paper_id)
        if paper is None:
            return JsonResponse({
                'success': False,
                'error': f"Paper not found: {paper_id}"
            })
        print(f'add_search_result: {paper_id} {paper}')

        review = Review(paper=paper, creator=user, comment=comment)
        review.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

@json_view
@require_login
def add_recommendation(request):
    data = request.json_data
    paper_id = data.get('paper_id')
    comment = data.get('comment')

    user = request.user.custom_user
    paper = Paper.objects.get(pk=paper_id)
    if paper is None:
        return JsonResponse({'success': False, 'error': f"Paper not found: {paper_id}"})

    review_list = Review.objects.filter(creator=user, paper=paper)
    if review_list.count() > 0:
        review = review_list[0]
        if review.comment != comment:
            review.comment = comment
            review.save()
    else:
        review = Review(paper=paper, creator=user, comment=comment)
        review.save()

    for recommendation in Recommendation.objects.filter(user=user, paper=paper, read_time__isnull=True):
        for label in recommendation.labels.all():
            if label not in review.labels.all():
                review.labels.add(label)
        recommendation.read_time = timezone.now()
        recommendation.save()

    return JsonResponse({'success': True})

@json_view
@require_login
def mark_read_recommendation(request):
    data = request.json_data
    paper_id = data.get('paper_id')

    user = request.user.custom_user
    paper = Paper.objects.get(pk=paper_id)
    if paper is None:
        return JsonResponse({'success': False, 'error': f"Paper not found: {paper_id}"})

    for recommendation in Recommendation.objects.filter(user=user, paper=paper, read_time__isnull=True):
        recommendation.read_time = timezone.now()
        recommendation.save()

    return JsonResponse({'success': True})

@json_view
@require_login
def restore_recommendation(request):
    data = request.json_data
    paper_id = data.get('paper_id')

    user = request.user.custom_user
    paper = Paper.objects.get(pk=paper_id)
    if paper is None:
        return JsonResponse({'success': False, 'error': f"Paper not found: {paper_id}"})

    for recommendation in Recommendation.objects.filter(user=user, paper=paper, read_time__isnull=False):
        recommendation.read_time = None
        recommendation.save()

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

        reviews = group.reviews.filter(delete_time__isnull=True)

        index = json_data.get('index', 0)
        if index == 0:
            stat = get_stat_this_month(reviews, group_name)
        elif index == 1:
            stat = get_stat_last_month(reviews, group_name)
        elif index == 2:
            stat = get_stat_all(reviews, group_name)
        elif index == 3:
            stat = get_stat_journal(reviews, group_name)
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

        reviews = group.reviews.filter(delete_time__isnull=True)

        stat_1 = get_stat_this_month(reviews, group_name, top_n=10)
        stat_2 = get_stat_last_month(reviews, group_name, top_n=10)
        stat_3 = get_stat_all(reviews, group_name, top_n=10)
        stat_4 = get_stat_journal(reviews, group_name, top_n=10)

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

def fetch_review_list(request):
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

        reviews = group.reviews.filter(delete_time__isnull=True)
        
        mode = json_data.get('mode', 0)
        if mode == 0: # all
            pass
        elif mode == 1: # this month
            reviews = reviews.filter(create_time__year=timezone.now().year, create_time__month=timezone.now().month)
        elif mode == 2: # last month
            year = timezone.now().year
            month = timezone.now().month
            if month == 1:
                year -= 1
                month = 12
            else:
                month -= 1
            reviews = reviews.filter(create_time__year=year, create_time__month=month)
        elif mode == 3: # user own
            token = json_data.get('token')
            user = UserSession.objects.get(token=token).user
            aliases = get_user_aliases(user)
            reviews = reviews.filter(creator__in=aliases)
        else:
            return JsonResponse({
                'success': False,
                'error': f"Invalid mode: {mode}"
            })

        reviews = reviews.order_by('-create_time', '-pk')

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
                'comment': p.comment,
                'doi': p.doi,
                'pmid': p.pmid,
                'arxiv_id': p.arxiv_id,
                'pmcid': p.pmcid,
            } for p in reviews[index:end_index]]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f"An error occurred: {e}"
        })

def fetch_review_info(request):
    json_data, response = parse_request(request)
    if json_data is None:
        return response

    token = json_data.get('token')
    if not token or not is_token_valid(token):
        return HttpResponseForbidden('Invalid or expired token')

    review_id = json_data.get('review_id')
    review_info, raw_dict = get_paper_info(review_id)
    if review_info is None:
        return JsonResponse({
            'success': False,
            "error": raw_dict
            })

    return JsonResponse({
        'success': True,
        "results": {
            "title": review_info.get('title', ''),
            "journal": review_info.get('journal', ''),
            "pub_year": review_info.get('pub_year', ''),
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

        review_id = json_data.get('review_id')
        title = json_data.get('title')
        pub_year = json_data.get('pub_year')
        journal = json_data.get('journal')
        nickname = json_data.get('nickname')
        comment = json_data.get('comment')

        review_info, raw_dict = get_paper_info(review_id)

        user = UserSession.objects.get(token=token).user
        if user.nickname != nickname:
            user.nickname = nickname
            user.save()

        now = timezone.now()
        review = Review(creator=user,
                      create_time=now,
                      update_time=now,
                      title=title or review_info['title'],
                      pub_year=pub_year or review_info['pub_year'],
                      journal=journal or review_info['journal'],
                      comment=comment)
        if review_info is not None:
            review.doi = review_info['id'].get('doi', '')
            review.pmid = review_info['id'].get('pmid', '')
            review.arxiv_id = review_info['id'].get('arxiv_id', '')
            review.pmcid = review_info['id'].get('pmcid', '')
            review.cnki_id = review_info['id'].get('cnki_id', '')
            review.authors = "\n".join(review_info.get('authors', []))
            review.abstract = review_info.get('abstract', '')
            review.urls = "\n".join(review_info.get('urls', []))

        review.save()

        group.reviews.add(review)
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

        review_id = json_data.get('review_id')
        print('review_id:', review_id)
        review, raw_dict = get_paper_info(review_id)
        print('review:', review)
        if review is None:
            return JsonResponse({"error": "review not found."})
        if review['abstract'] == "":
            review['abstract'] = get_abstract_by_doi(review['id']['doi'])

        in_msg = [
            {"role": "system", "content": "This is a scientific review reading assistance chatbot, using mainly Chinese to chat with user."},
            {"role": "system", "content": "You can ask questions about the review, or ask for a summary of the review."},
            {"role": "user", "content": f"Please summarize and comment on the following review in Chinese:\n\nTitle: {review['title']}\n\nAbstract:\n{review['abstract']}"},
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

def translate_text(s):
    try:
        AZURE_KEY = os.getenv('AZURE_KEY')
        AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
        AZURE_LOCATION = os.getenv('AZURE_LOCATION')
        AZURE_PATH = '/translate'
        constructed_url = AZURE_ENDPOINT + AZURE_PATH

        params = {
            'api-version': '3.0',
            'from': 'en',
            'to': 'zh-Hans',
        }

        headers = {
            'Ocp-Apim-Subscription-Key': AZURE_KEY,
            # location required if you're using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': AZURE_LOCATION,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }

        # You can pass more than one object in body.
        body = [{'text': s}]

        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        response = request.json()

        #print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
        return True, response[0]['translations'][0]['text']
    except Exception as e:
        return False, f"An error occurred: {e}"

def translate_title(request):
    print('translate_title:', request)
    paper_id = request.POST['paper_id']
    print('paper_id:', paper_id)

    paper = Paper.objects.get(pk=paper_id)
    pt = getattr(paper, 'translation', None)
    if pt and pt.title_cn:
        print(f'already translated: {pt.title_cn}')
        return JsonResponse({'success': True, 'answer': pt.title_cn})

    title = paper.title
    print('to translate:', title)

    success, result_text = translate_text(title)
    print(f'translate_text: {success} {result_text}')

    if not success:
        return JsonResponse({
            'success': False,
            'error': result_text
        })
    else:
        if not pt:
            pt = PaperTranslation(paper=paper, title_cn=result_text)
        else:
            pt.title_cn = result_text
        pt.save()
        return JsonResponse({'success': True, 'answer': result_text})

def translate_abstract(request):
    print('translate_abstract:', request)
    paper_id = request.POST['paper_id']
    print('paper_id:', paper_id)

    paper = Paper.objects.get(pk=paper_id)
    pt = getattr(paper, 'translation', None)
    if pt and pt.abstract_cn:
        print(f'already translated: {pt.abstract_cn}')
        return JsonResponse({'success': True, 'answer': pt.abstract_cn})

    abstract = paper.abstract
    print('to translate:', abstract)

    success, result_text = translate_text(abstract)
    print(f'translate_text: {success} {result_text}')

    if not success:
        return JsonResponse({
            'success': False,
            'error': result_text
        })
    else:
        if not pt:
            pt = PaperTranslation(paper=paper, abstract_cn=result_text)
        else:
            pt.abstract_cn = result_text
        pt.save()
        return JsonResponse({'success': True, 'answer': result_text})
