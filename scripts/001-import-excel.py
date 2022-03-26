#!/usr/bin/python
# 从Excel文件中导入当前所有记录
import os
import sys
import pandas as pd
import django

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

    df = pd.read_excel(sys.argv[1])
    #print(df)
    #print(len(df))

    label_name = "响马"
    if Label.objects.filter(name=label_name).count() == 0:
        xiangma = Label(name = label_name)
        xiangma.save()
    xiangma = Label.objects.filter(name=label_name)[0]

    for i in range(0, len(df)):
        if User.objects.filter(weixin_id=df['微信号'][i]).count() > 0:
            u = User.objects.filter(weixin_id=df['微信号'][i])[0]
        elif User.objects.filter(nickname=df['群友'][i]).count() > 0:
            u = User.objects.filter(nickname=df['群友'][i])[0]
        else:
            u = User(
                name = df['姓名'][i],
                nickname = df['群友'][i],
                weixin_id = df['微信号'][i],
                create_time = df['推荐日期'][i],
                last_login_time = df['推荐日期'][i])
            u.save()

        p = Paper(
            creator = u,
            create_time = df['推荐日期'][i],
            doi = df['DOI'][i],
            arxiv_id = df['arXiv'][i],
            journal = df['杂志'][i],
            publish_year = str(df['发表年份'][i]),
            title = df['文章标题'][i],
            comments = df['推荐理由'][i])

        if p.arxiv_id == '-':
            p.arxiv_id = ''
            modified = True
        if p.doi == '-':
            p.doi = ''
            modified = True
        if p.pmid == '-':
            p.pmid = ''
            modified = True
        if p.pmcid == '-':
            p.pmcid = ''
            modified = True
        if modified:
            p.save()

        p.save()
        xiangma.paper_set.add(p)

    xiangma.save()

if __name__ == '__main__':
    main()
