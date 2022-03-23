#!/usr/bin/python
# 更新部分字段，将“-”改为空
import os
import sys
import pandas as pd
import django

def main():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
    django.setup()

    from view.models import Paper
    #print(Paper.objects.all())

    for p in Paper.objects.all():
        if p.arxiv_id == '-':
            p.arxiv_id = ''
            p.save()
        elif p.doi == '-':
            p.doi = ''
            p.save()

if __name__ == '__main__':
    main()
