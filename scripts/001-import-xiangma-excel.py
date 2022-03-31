#!/usr/bin/python
# 从Excel文件中导入当前所有记录
import os
import sys
import pandas as pd
import django
import datetime
from django.utils import timezone
from backports import zoneinfo
import re

def main():
    # 载入Django相关环境
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
    django.setup()

    from view.models import Paper, Label, User
    #print(Paper.objects.all())

    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "<input.xlsx>")
        exit(1)

    df = pd.read_excel(sys.argv[1], na_filter=False)
    #print(df)

    label_name = "响马"
    if Label.objects.filter(name=label_name).count() == 0:
        xiangma = Label(name = label_name)
        xiangma.save()
    else:
        xiangma = Label.objects.filter(name=label_name)[0]

    # 获取当前时区信息
    tz_beijing = zoneinfo.ZoneInfo("Asia/Shanghai")

    for i in range(0, len(df)):
        # 根据时区信息初始化推荐日期
        the_date = timezone.make_aware(df['推荐日期'][i], tz_beijing)
        #print(the_date)

        weixin_id = df['微信号'][i]
        nickname = df['群友'][i]
        name = df['姓名'][i]
        if nickname == "":
            print("ERROR: empty user name and nickname in row " + str(i + 1))
            continue

        if weixin_id != "" and User.objects.filter(weixin_id=weixin_id).count() > 0:
            u = User.objects.filter(weixin_id=weixin_id)[0]
        elif User.objects.filter(nickname=nickname).count() > 0:
            u = User.objects.filter(nickname=nickname)[0]
        else:
            print("> Import user: '" + df['群友'][i] + "'")
            u = User(
                name = name,
                nickname = nickname,
                weixin_id = weixin_id,
                create_time = the_date,
                last_login_time = the_date)
            u.save()

        find_paper = Paper.objects.filter(creator=u, title=df['文章标题'][i])
        if find_paper.count() == 1:
            print(">> Update paper: '" + df['文章标题'][i] + "'")
            p = find_paper[0]
            p.create_time = the_date
            p.update_time = the_date

            p.doi = df['DOI'][i] if df['DOI'][i] != '-' else ''
            p.pmid = df['PMID'][i] if df['PMID'][i] != '-' else ''
            p.arxiv_id = df['arXiv'][i] if df['arXiv'][i] != '-' else ''
            p.pmcid = df['PMCID'][i] if df['PMCID'][i] != '-' else ''
            p.cnki_id = df['CNKI'][i] if df['CNKI'][i] != '-' else ''

            p.journal = df['杂志'][i]
            p.pub_date = datetime.date(df['发表年份'][i], 1, 1)
            p.title = df['文章标题'][i]
            p.authors = df['作者'][i]
            p.abstract = df['摘要'][i]
            p.keywords = df['关键词'][i]
            p.urls = df['URLs'][i]

            p.is_private = False
            p.comments = df['推荐理由'][i]
        else:
            Paper.objects.filter(creator=u, title=df['文章标题'][i]).delete()
            print(">> Import paper: '" + df['文章标题'][i] + "'")
            p = Paper(
                creator = u,
                create_time = the_date,
                update_time = the_date,

                doi = df['DOI'][i] if df['DOI'][i] != '-' else '',
                pmid = df['PMID'][i] if df['PMID'][i] != '-' else '',
                arxiv_id = df['arXiv'][i] if df['arXiv'][i] != '-' else '',
                pmcid = df['PMCID'][i] if df['PMCID'][i] != '-' else '',
                cnki_id = df['CNKI'][i] if df['CNKI'][i] != '-' else '',

                journal = df['杂志'][i],
                pub_date = datetime.date(df['发表年份'][i], 1, 1),
                title = df['文章标题'][i],
                authors = df['作者'][i],
                abstract = df['摘要'][i],
                keywords = df['关键词'][i],
                urls = df['URLs'][i],

                is_private = False,
                comments = df['推荐理由'][i])

        p.save()
        xiangma.paper_set.add(p)

    xiangma.save()

if __name__ == '__main__':
    main()
