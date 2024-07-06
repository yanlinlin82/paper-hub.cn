import os
import sys
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import Paper

def list_paper_index(output_csv):
    data = []
    for paper in Paper.objects.all():
        data.append({
            'id': paper.id,
            'pmid': paper.pmid,
            'doi': paper.doi,
            'journal': paper.journal,
            'pub_year': paper.pub_year,
            'title': paper.title
        })
    df = pd.DataFrame(data)
    df.to_excel(output_xlsx, index=False)
    print(f"Saved to {output_xlsx}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} <output.xlsx>')
        sys.exit(1)
    output_xlsx = sys.argv[1]
    list_paper_index(output_xlsx)
