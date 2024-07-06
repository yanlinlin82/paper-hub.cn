import os
import sys
import gzip
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paperhub.settings')
django.setup()

from view.models import PubMedIndex

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <deleted.pmids.gz> <cache/id-list/xxx.tsv>...")
        sys.exit(1)
    deleted_pmids_gz_file = sys.argv[1]

    print(f"Loading '{deleted_pmids_gz_file}' ...")
    deleted_pmids = set()
    with gzip.open(deleted_pmids_gz_file, 'rt') as file:
        for line in file:
            deleted_pmids.add(int(line.strip()))
    print(f"Loaded {len(deleted_pmids)} deleted PMIDs.")

    total = 0
    for id_list_tsv_file in sys.argv[2:]:
        print(f"Loading '{id_list_tsv_file}' ...")
        cnt = 0
        with open(id_list_tsv_file, 'rt') as file:
            for line in file:
                source, index, doi, pmid = line.strip().split('\t')
                source = int(source)
                index = int(index)
                pmid = int(pmid) + 1
                doi = None if doi == '' else doi
                if pmid in deleted_pmids:
                    continue

                rec = PubMedIndex.objects.filter(pmid=pmid)
                if rec.exists():
                    source_in_db = rec[0].source
                    index_in_db = rec[0].index
                    if source_in_db < source or (source_in_db == source and index_in_db < index):
                        rec.delete()
                    else:
                        continue

                if doi is not None:
                    rec = PubMedIndex.objects.filter(doi=doi)
                    if rec.exists():
                        source_in_db = rec[0].source
                        index_in_db = rec[0].index
                        if source_in_db < source or (source_in_db == source and index_in_db < index):
                            rec.delete()
                        else:
                            continue

                pi = PubMedIndex(source=source, index=index, doi=doi, pmid=pmid)
                pi.save()
                cnt += 1

        print(f"Loaded {cnt} PubMedIndex records from '{id_list_tsv_file}'.")
        total += cnt
    print(f"Total writed {total} PubMedIndex records into database.")
