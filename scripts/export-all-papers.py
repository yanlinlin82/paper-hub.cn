import os
import sys
import django
import pandas as pd
from datetime import datetime

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from core.models import Paper

def export_all_papers(output_xlsx):

    data = list(Paper.objects.all().values())

    for item in data:
        for key, value in item.items():
            if isinstance(value, datetime):
                item[key] = value.replace(tzinfo=None) # remove timezone info

    df = pd.DataFrame(data)
    df.to_excel(output_xlsx, index=False)
    print(f"Saved to {output_xlsx}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} <output.xlsx>')
        sys.exit(1)
    output_xlsx = sys.argv[1]
    export_all_papers(output_xlsx)
