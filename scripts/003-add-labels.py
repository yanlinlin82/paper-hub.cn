#!/usr/bin/python
# 为当前所有数据加入label
import os
import sys
import pandas as pd
import django

def main():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
    django.setup()

    from view.models import Label, Paper
    #print(Paper.objects.all())

    #xiangma = Label(name = "xiangma")
    #xiangma.save()
    xiangma = Label.objects.filter(name="xiangma")[0]

    for p in Paper.objects.all():
        xiangma.paper_set.add(p)
    xiangma.save()

if __name__ == '__main__':
    main()
