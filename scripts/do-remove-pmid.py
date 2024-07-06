import os
import sys
import gzip
import django
from django.db import transaction

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import PubMedIndex

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <deleted.pmids.gz>")
        sys.exit(1)
    deleted_pmids_gz_file = sys.argv[1]

    print(f"Loading '{deleted_pmids_gz_file}' ...")
    deleted_pmids = set()
    with gzip.open(deleted_pmids_gz_file, 'rt') as file:
        for line in file:
            deleted_pmids.add(int(line.strip()))
    print(f"Loaded {len(deleted_pmids)} deleted PMIDs.")

    chunk_size = 10000
    deleted_pmids_list = list(deleted_pmids)
    total_deleted_count = 0
    for i in range(0, len(deleted_pmids_list), chunk_size):
        chunk = deleted_pmids_list[i:i + chunk_size]
        with transaction.atomic():  # 使用事务保证一致性
            deleted_count = PubMedIndex.objects.filter(pmid__in=chunk).delete()[0]
            total_deleted_count += deleted_count
            if deleted_count > 0:
                print(f'Deleted {deleted_count} records in chunk {i // chunk_size + 1}')
    print(f"Total deleted {total_deleted_count} PubMedIndex records from database.")
