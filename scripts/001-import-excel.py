#!/usr/bin/python
# 从Excel文件中导入当前所有记录
import os
import sys
import pandas as pd
import django
import datetime
from django.utils import timezone
import re

def main():
    # 载入Django相关环境
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
    django.setup()

    from view.models import Paper, Label, User
    #from xiangma.models import Paper, Label, User
    #print(Paper.objects.all())

    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "<input.xlsx>")
        exit(1)

    df = pd.read_excel(sys.argv[1])
    #print(df)
    #print(len(df))

    label_name = "响马"
    if Label.objects.filter(name=label_name).count() == 0:
        xiangma = Label(name = label_name)
        xiangma.save()
    xiangma = Label.objects.filter(name=label_name)[0]

    # 获取当前时区信息
    tz = timezone.now().tzinfo

    for i in range(0, len(df)):
        # 根据时区信息初始化推荐日期
        the_date = df['推荐日期'][i].replace(tzinfo=tz)

        if User.objects.filter(weixin_id=df['微信号'][i]).count() > 0:
            u = User.objects.filter(weixin_id=df['微信号'][i])[0]
        elif User.objects.filter(nickname=df['群友'][i]).count() > 0:
            u = User.objects.filter(nickname=df['群友'][i])[0]
        else:
            print("> Import user: '" + df['群友'][i] + "'")
            u = User(
                name = df['姓名'][i],
                nickname = df['群友'][i],
                weixin_id = df['微信号'][i],
                create_time = the_date,
                last_login_time = the_date)
            u.save()

        print(">> Import paper: '" + df['文章标题'][i] + "'")
        p = Paper(
            creator = u,
            create_time = the_date,
            update_time = the_date,

            doi = df['DOI'][i] if df['DOI'][i] != '-' else '',
            pmid = '',
            arxiv_id = df['arXiv'][i] if df['arXiv'][i] != '-' else '',
            pmcid = '',

            journal = df['杂志'][i],
            title = df['文章标题'][i],
            pub_date = datetime.date(df['发表年份'][i], 1, 1),

            is_private = False,
            comments = re.sub(r"^\#paper", "", df['推荐理由'][i]))

        p.save()
        xiangma.paper_set.add(p)

    xiangma.save()

if __name__ == '__main__':
    main()
