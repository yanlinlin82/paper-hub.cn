import os
import sys
import numpy as np
import pandas as pd

def process(index_xlsx, output_xlsx, pubmed_dir):
    df = pd.read_excel(index_xlsx, dtype=str) # id,pmid,doi,journal,pub_year,title
    df['source'] = ''
    df['index'] = ''
    df['pmid_from_cache'] = ''
    df['doi_from_cache'] = ''
    df['updated'] = False

    deleted_pmids = set()
    deleted_pmids_gz = os.path.join(pubmed_dir, 'deleted.pmids.gz')
    if os.path.exists(deleted_pmids_gz):
        with open(deleted_pmids_gz, 'r') as f:
            for line in f.readlines():
                deleted_pmids.add(line.strip())

    pmid_to_index = {}
    doi_to_index = {}
    for index, row in df.iterrows():
        pmid_to_index[row['pmid']] = index
        doi_to_index[row['doi']] = index

    pubmed_cache_dir = os.path.join(pubmed_dir, 'cache', 'id-list')
    files = sorted(os.listdir(pubmed_cache_dir), reverse=True)
    cnt, total = 0, len(files)
    for file in files:
        cnt += 1
        if file.endswith('.tsv'):
            with open(os.path.join(pubmed_cache_dir, file), 'r') as f:
                cnt2 = 0
                for line in f.readlines():
                    source, index, doi, pmid = line.strip().split('\t')
                    if pmid in deleted_pmids:
                        continue
                    i = None
                    if pmid in pmid_to_index:
                        i = pmid_to_index[pmid]
                    elif doi in doi_to_index:
                        i = doi_to_index[doi]

                    if i is not None and not df.loc[i, 'updated']:
                        cnt2 += 1
                        print(f"Processing ({cnt}/{total}) {file} - row:{i}, cnt:{cnt2}, {source}[{index}], pmid:{pmid} doi:{doi}")
                        df.loc[i, 'source'] = source
                        df.loc[i, 'index'] = index
                        df.loc[i, 'pmid_from_cache'] = pmid
                        df.loc[i, 'doi_from_cache'] = doi
                        df.loc[i, 'updated'] = True

                        if not pd.isna(df.loc[i, 'pmid']) and pmid != "" and df.loc[i, 'pmid'] != pmid:
                            print(f"Warning: PMID mismatch for paper (id:{df.loc[i, 'id']}, doi:{df.loc[i, 'doi']}): '{df.loc[i, 'pmid']}' vs '{pmid}'")
                        if not pd.isna(df.loc[i, 'doi']) and doi != "" and df.loc[i, 'doi'] != doi:
                            print(f"Warning: DOI mismatch for paper (id:{df.loc[i, 'id']}, pmid:{df.loc[i, 'pmid']}): '{df.loc[i, 'doi']}' vs '{doi}'")

    df.to_excel(output_xlsx, index=False)
    print(f"Saved to {output_xlsx}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f'Usage: python {sys.argv[0]} <index.xlsx> <output.xlsx> <pubmed-dir>')
        sys.exit(1)
    input_xlsx = sys.argv[1]
    output_xlsx = sys.argv[2]
    pubmed_dir = sys.argv[3]

    process(input_xlsx, output_xlsx, pubmed_dir)
