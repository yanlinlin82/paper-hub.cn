import os
import sys
import pandas as pd
import django

# 设置 Django 项目配置模块的路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import PaperTracking, UserProfile, Paper, Label, Recommendation, RecommendationDetails

def check_pd_na(x):
    if pd.isna(x):
        return ''
    return x

def import_excel(excel_file):
    u = UserProfile.objects.get(pk=1)
    a = pd.read_excel(excel_file) # eg. "/work/Research/PubMed-Mining/out.xlsx"
    # labels	title	journal	date	doi	pmid	author	institutes	abstract	keywords

    print(f'Importing {len(a)} recommendations for user {u.nickname} ...')
    cnt = 0
    new = 0
    new2 = 0
    detail = 0
    detail_succ = 0
    for _, i in a.iterrows():
        cnt += 1
        if cnt % 100 == 0:
            print(f'Processed {cnt} recommendations ...')

        doi = check_pd_na(i['doi'])
        pmid = check_pd_na(i['pmid'])
        paper_list = Paper.objects.filter(doi = doi, pmid = pmid)
        if len(paper_list) == 0:
            pub_year = None
            pub_date = ''
            if not pd.isna(i['date']):
                pub_year = int(i['date'])
                pub_date = str(i['date'])
            p = Paper(journal = check_pd_na(i['journal']), pub_year = pub_year, pub_date = pub_date, \
                    title = check_pd_na(i['title']), authors = check_pd_na(i['author']), institutes = check_pd_na(i['institutes']), \
                    abstract = check_pd_na(i['abstract']), keywords = check_pd_na(i['keywords']), \
                    doi = doi, pmid = pmid)
            p.save()
            new += 1
        else:
            p = paper_list[0]

        r_list = Recommendation.objects.filter(paper = p, user = u)
        if len(r_list) == 0:
            r = Recommendation(paper = p, user = u)
            r.save()
            new2 += 1
        else:
            r = r_list[0]

        for label_item in i['labels'].split('\n'):
            detail += 1
            label_list = Label.objects.filter(user = u, name = label_item)
            if len(label_list) == 0:
                print(f'Error: Cannot find label {label_item} for user {u.nickname}', file = sys.stderr)
                continue
            l = label_list[0]

            tracking_list = PaperTracking.objects.filter(user = u, label = l)
            if len(tracking_list) > 0:
                t = tracking_list[0]

                d = RecommendationDetails(recommendation = r, recommend_time = r.create_time, \
                                        type = t.type, value = t.value, label = t.label, memo = t.memo)
                d.save()
                detail_succ += 1

    print(f'Imported {cnt} recommendations, {new} new papers, {new2} new recommendations, {detail} details, {detail_succ} details saved.')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <excel_file>', file = sys.stderr)
        sys.exit(1)

    import_excel(sys.argv[1])
