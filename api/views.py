from django.http import JsonResponse
from django.shortcuts import render

from view.models import Paper, User
from view.paper import *

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
        return JsonResponse({"error": "user '" + user + "' not found."}, status=200)
    else:
        return JsonResponse({
            "error": "",
            "query": user,
            "results": {
                "nickname": u[0].nickname,
                "name": u[0].name,
                "weixin_id": u[0].weixin_id,
                "username": u[0].username,
            }}, status=200)

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
        return JsonResponse({"error": raw_dict})

    return JsonResponse({
        "error": "",
        "query": id,
        "raw": raw_dict,
        "results": {
            "doi": paper_info['doi'],
            "title": paper_info['title'],
            "journal": paper_info['journal'],
            "pub_date": paper_info['pub_date'],
            "authors": paper_info['authors'],
            "abstract": paper_info['abstract'],
            "urls": paper_info['urls'],
        }}, status=200)
