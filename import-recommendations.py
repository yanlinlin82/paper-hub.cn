import os
import sys
import pandas as pd
import django

# 设置 Django 项目配置模块的路径
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import PaperTracking, UserProfile, Paper, Label, Recommendation, RecommendationDetails

def import_excel(excel_file):

    # 导入推荐数据，都按照我自己的用户来导入
    u = UserProfile.objects.get(pk=1)

    # 读取 Excel 文件，例如："/work/Research/PubMed-Mining/out.xlsx"
    # 字段列表依次为：
    #   labels, title, journal, pub_date, pub_year, doi, pmid, author, institutes, abstract, keywords, language
    a = pd.read_excel(excel_file)
    a.fillna('', inplace = True)

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

        paper_list = Paper.objects.filter(doi=i['doi'], pmid=i['pmid'])
        if len(paper_list) == 0:
            p = Paper(journal=i['journal'], pub_date=i['pub_date'], pub_year=i['pub_year'], \
                      title=i['title'], authors=i['author'], institutes=i['institutes'], \
                      abstract=i['abstract'], keywords=i['keywords'], \
                      doi=i['doi'], pmid=i['pmid'], language=i['language'])
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
