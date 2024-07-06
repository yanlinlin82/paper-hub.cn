import os
import sys
import pandas as pd
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import PaperTracking, UserProfile, Paper, Label, Recommendation

def import_excel(source_id, excel_file):

    # 导入推荐数据，都按照我自己的用户来导入
    u = UserProfile.objects.get(pk=1)

    # 读取 Excel 文件，例如："/work/Research/PubMed-Mining/out.xlsx"
    # 字段列表依次为：
    #   labels, title, journal, pub_date, pub_year, doi, pmid, author, institutes, abstract, keywords, language
    a = pd.read_excel(excel_file)
    a.fillna('', inplace = True)

    print(f'Importing {len(a)} recommendations for source {source_id} and user {u.nickname} ...')
    cnt = {
        'total': 0,
        'new_paper': 0,
        'new_recommendation': 0,
        'label_updated': 0,
    }

    for _, i in a.iterrows():
        cnt['total'] += 1
        if cnt['total'] % 100 == 0:
            print(f"Processed {cnt['total']} recommendations ...")

        paper_list = Paper.objects.filter(doi=i['doi'], pmid=i['pmid'])
        if len(paper_list) == 0:
            p = Paper(journal=i['journal'], pub_date=i['pub_date'], pub_year=i['pub_year'], \
                      title=i['title'], authors=i['author'], institutes=i['institutes'], \
                      abstract=i['abstract'], keywords=i['keywords'], \
                      doi=i['doi'], pmid=i['pmid'], language=i['language'])
            p.save()
            cnt['new_paper'] += 1
        else:
            p = paper_list[0]
            p.journal = i['journal']
            p.pub_date = i['pub_date']
            p.pub_year = i['pub_year']
            if p.title != i['title']:
                p.title = i['title']
                if hasattr(p, 'translation'):
                    p.translation.title_cn = ''
                    p.translation.save()
            p.authors = i['author']
            p.institutes = i['institutes']
            if p.abstract != i['abstract']:
                p.abstract = i['abstract']
                if hasattr(p, 'translation'):
                    p.translation.abstract_cn = ''
                    p.translation.save()
            p.keywords = i['keywords']
            p.language = i['language']
            p.save()

        r_list = Recommendation.objects.filter(paper = p, user = u, source = source_id)
        if len(r_list) == 0:
            r = Recommendation(paper = p, user = u, source = source_id)
            r.save()
            cnt['new_recommendation'] += 1
        else:
            r = r_list[0]

        any_change = False
        for label_item in [l for l in i['labels'].split('\n') if l]:
            label = Label.objects.filter(user = u, name = label_item)
            if len(label) > 0:
                if len(r.labels.filter(pk = label[0].pk)) == 0:
                    r.labels.add(label[0])
                    cnt['label_updated'] += 1
                    any_change = True
        if any_change:
            r.delete_time = None
            r.save()

    print(f"Imported {cnt['total']} recommendations, {cnt['new_paper']} new papers, {cnt['new_recommendation']} new recommendations, {cnt['label_updated']} labels updated.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <source_id> <excel_file>', file = sys.stderr)
        sys.exit(1)

    import_excel(sys.argv[1], sys.argv[2])
