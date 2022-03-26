#!/usr/bin/python
# 从Excel文件中导入当前所有记录
import os
import sys
import pandas as pd
import django

def main():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    #print(sys.path)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
    django.setup()

    from view.models import Paper
    #print(Paper.objects.all())

    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "<input.xlsx>")
        exit(1)

    df = pd.read_excel(sys.argv[1])
    #print(df)
    #print(len(df))

    for i in range(0, len(df)):
        p = Paper(
            creator = df['群友'][i],
            creator_weixin_id = df['微信号'][i],
            create_time = df['推荐日期'][i],
            doi = df['DOI'][i],
            arxiv_id = df['arXiv'][i],
            journal = df['杂志'][i],
            publish_year = str(df['发表年份'][i]),
            title = df['文章标题'][i],
            comments = df['推荐理由'][i])
        #print(p)
        p.save()

if __name__ == '__main__':
    main()
