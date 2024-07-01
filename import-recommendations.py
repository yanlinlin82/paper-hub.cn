import os
import sys
import pandas as pd
import django

# 设置 Django 项目配置模块的路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import PaperTracking, UserProfile, Paper, Label, Recommendation

u = UserProfile.objects.get(pk=1)
a = pd.read_excel("/work/Research/PubMed-Mining/out.xlsx")
# labels	title	journal	date	doi	pmid	author	institutes	abstract	keywords

for _, i in a.iterrows():
    paper_list = Paper.objects.filter(doi = i['doi'])
    if len(paper_list) == 0:
        pub_year = None
        pub_date = ''
        if not pd.isna(i['date']):
            pub_year = int(i['date'])
            pub_date = str(i['date'])
        p = Paper(journal = i['journal'], pub_year = pub_year, pub_date = pub_date, \
                  title = i['title'], authors = i['author'], institutes = i['institutes'], \
                  abstract = i['abstract'], keywords = i['keywords'], \
                  doi = i['doi'], pmid = i['pmid'])
        p.save()
    else:
        p = paper_list[0]

    r_list = Recommendation.objects.filter(paper = p, user = u)
    if len(r_list) == 0:
        r = Recommendation(paper = p, user = u)
        r.save()
    else:
        r = r_list[0]

    for label_item in i['labels'].split('\n'):
        label_list = Label.objects.filter(user = u, name = label_item)
        if len(label_list) == 0:
            print(f'Error: Cannot find label {label_item} for user {u.nickname}', file = sys.stderr)
            continue
        l = label_list[0]

        tracking_list = PaperTracking.objects.filter(user = u, label = l)
        if len(tracking_list) == 0:
            print(f'Error: Cannot find tracking rule for label {label_item} for user {u.nickname}', file = sys.stderr)
            continue
        r.trackings.add(tracking_list[0])
        r.save()
