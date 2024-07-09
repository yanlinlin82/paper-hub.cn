import os
import sys
import pandas as pd
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from core.models import PaperTracking, UserProfile, Paper, Label, Recommendation

def ms(s, sep=', '): # print multi-line string
    return sep.join(s.split('\n'))

def import_excel(source_id, excel_file):

    # 导入推荐数据，都按照我自己的用户来导入
    u = UserProfile.objects.get(pk=1)

    # 读取 Excel 文件，例如："/work/Research/PubMed-Mining/out.xlsx"
    # 字段列表依次为：
    #   labels, title, journal, pub_date, pub_year, doi, pmid, author, affiliations, abstract, keywords, language
    a = pd.read_excel(excel_file)
    a.fillna('', inplace = True)

    print(f'Importing {len(a)} recommendations for source {source_id} and user {u.nickname} ...')
    r_total, r_new, r_update, p_new, p_update = 0, 0, 0, 0, 0
    for _, i in a.iterrows():
        r_total += 1
        if r_total % 100 == 0:
            print(f"Processed {r_total} recommendations ...")

        paper_list = Paper.objects.filter(doi=i['doi'], pmid=i['pmid'])
        if len(paper_list) == 0:
            p = Paper(journal=i['journal'], pub_date=i['pub_date'], pub_year=i['pub_year'], \
                      title=i['title'], authors=i['author'], affiliations=i['affiliations'], \
                      abstract=i['abstract'], keywords=i['keywords'], \
                      doi=i['doi'], pmid=i['pmid'], language=i['language'])
            p.save()
            p_new += 1
        else:
            p = paper_list[0]
            any_change = False
            if p.journal != i['journal']:
                print(f"  -> paper({p.pk}).journal: '{p.journal}' -> '{i['journal']}'")
                p.journal = i['journal']
                any_change = True
            if p.pub_date != i['pub_date']:
                print(f"  -> paper({p.pk}).pub_date: '{p.pub_date}' -> '{i['pub_date']}'")
                p.pub_date = i['pub_date']
                any_change = True
            if p.pub_year != i['pub_year']:
                print(f"  -> paper({p.pk}).pub_year: '{p.pub_year}' -> '{i['pub_year']}'")
                p.pub_year = i['pub_year']
                any_change = True
            if p.title != i['title']:
                print(f"  -> paper({p.pk}).title: '{p.title}' -> '{i['title']}'")
                p.title = i['title']
                any_change = True
                if hasattr(p, 'translation'):
                    p.translation.title_cn = ''
                    p.translation.save()
            if p.authors != i['author']:
                print(f"  -> paper({p.pk}).authors: '{ms(p.authors)}' -> '{ms(i['author'])}'")
                p.authors = i['author']
                any_change = True
            if p.affiliations != i['affiliations']:
                print(f"  -> paper({p.pk}).affiliations: '{ms(p.affiliations)}' -> '{ms(i['affiliations'])}'")
                p.affiliations = i['affiliations']
                any_change = True
            if p.abstract != i['abstract']:
                print(f"  -> paper({p.pk}).abstract: '{ms(p.abstract, ' ')}' -> '{ms(i['abstract'], ' ')}'")
                p.abstract = i['abstract']
                any_change = True
                if hasattr(p, 'translation'):
                    p.translation.abstract_cn = ''
                    p.translation.save()
            if p.keywords != i['keywords']:
                print(f"  -> paper({p.pk}).keywords: '{ms(p.keywords)}' -> '{ms(i['keywords'])}'")
                p.keywords = i['keywords']
                any_change = True
            if p.language != i['language']:
                print(f"  -> paper({p.pk}).language: '{p.language}' -> '{i['language']}'")
                p.language = i['language']
                any_change = True
            if any_change:
                p.save()
                p_update += 1

        r_list = Recommendation.objects.filter(paper = p, user = u, source = source_id)
        if len(r_list) == 0:
            r = Recommendation(paper = p, user = u, source = source_id)
            r.save()
            r_new += 1
        else:
            if len(r_list) > 1:
                print(f"Warning: multiple recommendations found for paper {p.pk} and user {u.pk} and source {source_id}.")
            r = r_list[0]

        any_change = False
        for label_item in [l for l in i['labels'].split('\n') if l]:
            label = Label.objects.filter(user = u, name = label_item)
            if len(label) > 0:
                if len(r.labels.filter(pk = label[0].pk)) == 0:
                    r.labels.add(label[0])
                    any_change = True
        if any_change:
            r.read_time = None
            r.save()
            r_update += 1

    print(f"Imported: {r_total} recommendations ({r_new} new, {r_update - r_new} update), {p_new + p_update} papers ({p_new} new, {p_update} update).")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <source_id> <excel_file>', file = sys.stderr)
        sys.exit(1)

    import_excel(sys.argv[1], sys.argv[2])
