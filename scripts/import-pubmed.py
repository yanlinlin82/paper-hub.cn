import os
import sys
import re
import argparse
from datetime import datetime
from lxml import etree
import django

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from core.models import Paper, Journal, PaperReference, PubMedIndex, PaperTracking, Recommendation, Label
from core.paper import PaperInfo

def match_journal(name):
    journal = Journal.objects.filter(name__iexact=name).first()
    if not journal:
        journal = Journal.objects.filter(abbreviation__iexact=name).first()
    return journal

def get_file_modification_time(file_path):
    modification_time = os.path.getmtime(file_path)
    mod_time_dt = datetime.fromtimestamp(modification_time)
    formatted_time = mod_time_dt.strftime('%Y%m%d')
    return formatted_time

def update_journal_info(paper):
    journal_name = paper.journal.strip()
    journal_name = re.sub(r'\s+', ' ', journal_name)
    if not journal_name:
        return

    journal = match_journal(journal_name)
    if not journal:
        journal_name_2 = re.sub(r'\s+:\s+.*$', '', journal_name)
        journal = match_journal(journal_name_2)
        if not journal:
            journal_name_3 = re.sub(r'the journal of', 'journal of', journal_name, flags=re.IGNORECASE)
            journal = match_journal(journal_name_3)

    if journal:
        paper.journal_abbreviation = journal.abbreviation
        paper.journal_impact_factor = journal.impact_factor
        paper.journal_impact_factor_quartile = journal.impact_factor_quartile

def J(s):
    return ', '.join(s.split('\n'))

class PubMedXMLFile:
    def __init__(self):
        self.pubmed_xml_gz = None
        self.source = None
        self.tree = None
        self.root = None
        self.num_articles = 0
        self.pmids_to_remove = set()

    def load(self, pubmed_dir, source):
        pubmed_part = 'baseline' if source < 1220 else 'updatefiles'
        self.pubmed_xml_gz = os.path.join(pubmed_dir, pubmed_part, f'pubmed24n{source}.xml.gz')
        if not os.path.exists(self.pubmed_xml_gz):
            print(f"File not found: {self.pubmed_xml_gz}")
            return False

        print(f"Loading '{self.pubmed_xml_gz}'...")
        self.source = source
        self.tree = etree.parse(self.pubmed_xml_gz)
        self.root = self.tree.getroot()

        self.num_articles = int(self.root.xpath('count(/PubmedArticleSet/PubmedArticle)'))

        for pmid in self.root.xpath('/PubmedArticleSet/DeleteCitation/PMID/text()'):
            self.pmids_to_remove.add(int(pmid))

        print(f"Loading done. There are {self.num_articles} articles and {len(self.pmids_to_remove)} removed PMIDs.")
        return True

    def update_references(self, paper, paper_info, type, run, verbose):
        cc_list = paper_info.get_references(type)
        if verbose:
            print(f"  {type} for paper ({paper.pk}): {len(cc_list)}")
        total, new, updated, deleted = len(cc_list), 0, 0, 0
        if cc_list:
            if paper.pk is None:
                pr_list = []
                pr_cnt = 0
            else:
                pr_list = PaperReference.objects.filter(paper=paper, type=type).order_by('index')
                pr_cnt = pr_list.count()
            for index, cc in enumerate(cc_list):
                if index < pr_cnt:
                    pr = pr_list[index]
                    any_change = False
                    if pr.index != index + 1:
                        if verbose:
                            print(f"    [{index+1}] index: {pr.index} -> {index + 1}")
                        pr.index = index + 1
                        any_change = True
                    ref_type = cc.get('ref_type', '') or ''
                    if pr.ref_type != ref_type:
                        if verbose:
                            print(f"    [{index+1}] ref_type: '{pr.ref_type}' -> '{ref_type}'")
                        pr.ref_type = ref_type
                        any_change = True
                    citation = cc.get('citation', '') or ''
                    if pr.citation != citation:
                        if verbose:
                            print(f"    [{index+1}] citation: '{pr.citation}' -> '{citation}'")
                        pr.citation = citation
                        any_change = True
                    doi = cc.get('doi', '') or ''
                    if pr.doi != doi:
                        if verbose:
                            print(f"    [{index+1}] doi: '{pr.doi}' -> '{doi}'")
                        pr.doi = doi
                        any_change = True
                    pmid = cc.get('pmid', '') or ''
                    if pr.pmid != pmid:
                        if verbose:
                            print(f"    [{index+1}] pmid: '{pr.pmid}' -> '{pmid}'")
                        pr.pmid = pmid
                        any_change = True
                    pmcid = cc.get('pmcid', '') or ''
                    if pr.pmcid != pmcid:
                        if verbose:
                            print(f"    [{index+1}] pmcid: '{pr.pmcid}' -> '{pmcid}'")
                        pr.pmcid = pmcid
                        any_change = True
                    if any_change:
                        if run:
                            pr.save()
                        updated += 1
                else:
                    if verbose:
                        print(f"    [{index+1}] New reference {cc}")
                    if run:
                        pr = PaperReference(
                            paper=paper,
                            type=type,
                            ref_type=cc.get('ref_type', '') or '',
                            index=index + 1,
                            citation=cc.get('citation', '') or '',
                            doi=cc.get('doi', '') or '',
                            pmid=cc.get('pmid', '') or '',
                            pmcid=cc.get('pmcid', '') or '',
                        )
                        pr.save()
                    new += 1
            if total < pr_cnt:
                deleted = pr_cnt - total
                if run:
                    pr_list.filter(index__gt=total).delete()
            if verbose:
                print(f"  {type} for paper ({paper.pk}): {total} total, {new} new, {updated} updated, {deleted} deleted")
        return (new > 0 or updated > 0 or deleted > 0)

    def _update_paper_info(self, mode, paper_info, index, run, verbose):
        if paper_info.pmid in self.pmids_to_remove:
            print(f"Skip removed PMID: {paper_info.pmid}")
            return None, False, False

        pi_list = PubMedIndex.objects.filter(source=self.source, index=index)
        if pi_list.exists():
            pi = pi_list[0]
            any_change = False
            if pi.pmid != paper_info.pmid:
                pi.pmid = paper_info.pmid
                any_change = True
            if pi.doi != paper_info.doi:
                pi.doi = paper_info.doi
                any_change = True
            if any_change:
                if run:
                    pi.save()
                print(f"Updated PubMedIndex record: source {self.source}, index {index}, pmid {paper_info.pmid}, doi {paper_info.doi}")
        else:
            print(f"Added PubMedIndex record: source {self.source}, index {index}, pmid {paper_info.pmid}, doi {paper_info.doi}")
            pi = PubMedIndex.objects.create(source=self.source, index=index, pmid=paper_info.pmid, doi=paper_info.doi)
            if run:
                pi.save()

        if mode == 'update-index':
            return None, False, False

        new, updated = False, False
        if paper_info.pmid is not None:
            if Paper.objects.filter(pmid=paper_info.pmid).exists():
                paper = Paper.objects.get(pmid=paper_info.pmid)
                updated = True
                print(f"Select paper [{index}]({paper.pk}) for PMID {paper_info.pmid} to update, {paper_info}")
            else:
                paper = Paper(pmid=paper_info.pmid)
                if run:
                    paper.save()
                new = True
                print(f"Create new paper [{index}] for PMID {paper_info.pmid}, {paper_info}")
        elif paper_info.doi is not None:
            if Paper.objects.filter(doi=paper_info.doi).exists():
                paper = Paper.objects.get(doi=paper_info.doi)
                updated = True
                print(f"Select paper [{index}]({paper.pk}) for DOI {paper_info.doi} to update, {paper_info}")
            else:
                paper = Paper(doi=paper_info.doi)
                if run:
                    paper.save()
                new = True
                print(f"Create new paper [{index}] for DOI {paper_info.doi}, {paper_info}")
        else:
            paper = Paper()
            if run:
                paper.save()
            new = True
            print(f"Create new paper [{index}] {paper_info}")

        any_change = False
        if paper_info.journal is not None:
            if paper.journal != paper_info.journal:
                if verbose:
                    print(f"  [{index}]journal: '{paper.journal}' -> '{paper_info.journal}'")
                paper.journal = paper_info.journal
                update_journal_info(paper)
                any_change = True
        if paper_info.pub_date is not None:
            if paper.pub_date != paper_info.pub_date:
                if verbose:
                    print(f"  [{index}]pub_date: '{paper.pub_date}' -> '{paper_info.pub_date}'")
                paper.pub_date = paper_info.pub_date
                any_change = True
        if paper_info.pub_year is not None:
            if paper.pub_year != paper_info.pub_year:
                if verbose:
                    print(f"  [{index}]pub_year: '{paper.pub_year}' -> '{paper_info.pub_year}'")
                paper.pub_year = paper_info.pub_year
                any_change = True
        if paper_info.title is not None:
            if paper.title != paper_info.title:
                if verbose:
                    print(f"  [{index}]title: '{paper.title}' -> '{paper_info.title}'")
                paper.title = paper_info.title
                any_change = True
        if paper_info.authors is not None:
            authors = '\n'.join(paper_info.authors)
            if paper.authors != authors:
                if verbose:
                    print(f"  [{index}]authors: '{J(paper.authors)}' -> '{J(authors)}'")
                paper.authors = authors
                any_change = True
        if paper_info.affiliations is not None:
            affiliations = '\n'.join(paper_info.affiliations)
            if paper.affiliations != affiliations:
                if verbose:
                    print(f"  [{index}]affiliations: '{J(paper.affiliations)}' -> '{J(affiliations)}'")
                paper.affiliations = affiliations
                any_change = True
        if paper_info.abstract is not None:
            if paper.abstract != paper_info.abstract:
                if verbose:
                    print(f"  [{index}]abstract: '{J(paper.abstract)}' -> '{J(paper_info.abstract)}'")
                paper.abstract = paper_info.abstract
                any_change = True
        if paper_info.keywords is not None:
            keywords = '\n'.join(paper_info.keywords)
            if paper.keywords != keywords:
                if verbose:
                    print(f"  [{index}]keywords: '{J(paper.keywords)}' -> '{J(keywords)}'")
                paper.keywords = keywords
                any_change = True
        if paper_info.doi is not None:
            if paper.doi != paper_info.doi:
                if verbose:
                    print(f"  [{index}]doi: '{paper.doi}' -> '{paper_info.doi}'")
                paper.doi = paper_info.doi
                any_change = True
        if paper_info.pmid is not None:
            if paper.pmid != paper_info.pmid:
                if verbose:
                    print(f"  [{index}]pmid: '{paper.pmid}' -> '{paper_info.pmid}'")
                paper.pmid = paper_info.pmid
                any_change = True
        if paper_info.arxiv_id is not None:
            if paper.arxiv_id != paper_info.arxiv_id:
                if verbose:
                    print(f"  [{index}]arxiv_id: '{paper.arxiv_id}' -> '{paper_info.arxiv_id}'")
                paper.arxiv_id = paper_info.arxiv_id
                any_change = True
        if paper_info.pmcid is not None:
            if paper.pmcid != paper_info.pmcid:
                if verbose:
                    print(f"  [{index}]pmcid: '{paper.pmcid}' -> '{paper_info.pmcid}'")
                paper.pmcid = paper_info.pmcid
                any_change = True
        if paper_info.cnki_id is not None:
            if paper.cnki_id != paper_info.cnki_id:
                if verbose:
                    print(f"  [{index}]cnki_id: '{paper.cnki_id}' -> '{paper_info.cnki_id}'")
                paper.cnki_id = paper_info.cnki_id
                any_change = True
        if paper_info.language is not None:
            if paper.language != paper_info.language:
                if verbose:
                    print(f"  [{index}]language: '{paper.language}' -> '{paper_info.language}'")
                paper.language = paper_info.language
                any_change = True
        if any_change:
            if run:
                paper.save()
            if verbose:
                print(f"  Saved paper [{index}]({paper.pk})")
        else:
            if verbose:
                print(f"  No change for paper [{index}]({paper.pk})")

        any_ref_changed_1 = self.update_references(paper, paper_info, 'CommentsCorrectionsList', run, verbose)
        any_ref_changed_2 = self.update_references(paper, paper_info, 'ReferenceList', run, verbose)
        return paper, new, (updated and (any_change or any_ref_changed_1 or any_ref_changed_2))

    def scan_rules_for_single_paper(self, index, paper_info, mode, rules, run, verbose, cnt):
        labels = []
        if mode == 'default':
            for rule_item in rules:
                matched = False
                if rule_item['type'] == 'keyword':
                    if self.match_keyword(paper_info, rule_item['value']):
                        matched = True
                elif rule_item['type'] == 'author':
                    if self.match_author(paper_info, rule_item['value']):
                        matched = True
                elif rule_item['type'] == 'affiliation':
                    if self.match_affiliation(paper_info, rule_item['value']):
                        matched = True
                elif rule_item['type'] == 'journal':
                    if self.match_journal(paper_info, rule_item['value']):
                        matched = True
                elif rule_item['type'] == 'cite':
                    if self.match_cite(paper_info, rule_item['value']):
                        matched = True
                if matched:
                    labels.append(rule_item['label'])

            if not labels:
                if verbose:
                    print(f"Skip paper [{index}]({paper_info}), since no any rule matched.")
                return

            print(f"Found matched paper [{index}]({paper_info})")
            print(f"  [{index}]matched labels:", ', '.join([i.name for i in labels]))

        if mode == 'update-info':
            if verbose:
                print(f"Force update paper [{index}]({paper_info}), skip rule matching")

        cnt['paper']['matched'] += 1
        paper, new, updated = self._update_paper_info(mode, paper_info, index, run, verbose)
        if paper is None:
            return
        if new:
            cnt['paper']['new'] += 1
        if updated:
            cnt['paper']['updated'] += 1

        if mode == 'default':
            cnt['recommendation']['total'] += 1
            r_list = Recommendation.objects.filter(paper=paper, source=self.generate_source_text(), user=rule_item['user'])
            if r_list.exists():
                if verbose:
                    print(f"  Recommendation already exists for paper [{index}]({paper.pk})")
                recommendation = r_list[0]
            else:
                cnt['recommendation']['new'] += 1
                recommendation = Recommendation(
                    paper=paper,
                    source=self.generate_source_text(),
                    user=rule_item['user'],
                )
                if run:
                    recommendation.save()
                print(f"  Added recommendation ({recommendation.pk}) for paper [{index}]({paper.pk})")
            any_changed = False
            for label in labels:
                if label not in recommendation.labels.all():
                    any_changed = True
                    print(f"    Add label '{label.name}' to recommendation ({recommendation.pk})")
                    if run:
                        recommendation.labels.add(label)
            if any_changed and r_list.exists():
                cnt['recommendation']['updated'] += 1

    def scan_rules(self, mode, rules, run, verbose, cnt, start=None, end=None):
        if start is None and end is None:
            for index, article_node in enumerate(self.root.xpath('/PubmedArticleSet/PubmedArticle')):
                cnt['paper']['total'] += 1

                if verbose and (index + 1) % 1000 == 0:
                    print(f"Processing article {index + 1} / {self.num_articles}")

                paper_info = PaperInfo(article_node)
                self.scan_rules_for_single_paper(index + 1, paper_info, mode, rules, run, verbose, cnt)
        elif start is not None and end is not None:
            for index in range(start, end + 1):
                cnt['paper']['total'] += 1

                article_node = self.root.xpath(f'/PubmedArticleSet/PubmedArticle[{index}]')[0]

                paper_info = PaperInfo(article_node)
                self.scan_rules_for_single_paper(index, paper_info, mode, rules, run, verbose, cnt)
        else:
            index = start or end
            cnt['paper']['total'] += 1

            article_node = self.root.xpath(f'/PubmedArticleSet/PubmedArticle[{index}]')[0]

            paper_info = PaperInfo(article_node)
            self.scan_rules_for_single_paper(index, paper_info, mode, rules, run, verbose, cnt)

    def generate_source_text(self):
        # eg. 'pubmed24n1453.20240628'
        return f'pubmed24n{self.source}.' + get_file_modification_time(self.pubmed_xml_gz)

    def match_keyword(self, paper_info, keyword):
        pattern = r'\b{}\b'.format(re.escape(keyword))
        return re.search(pattern, paper_info.title, re.IGNORECASE) \
            or re.search(pattern, paper_info.abstract, re.IGNORECASE) \
            or any(re.search(pattern, k, re.IGNORECASE) for k in paper_info.keywords)

    '''
    IndexError: b'
<Author ValidYN="Y">\n
            <LastName>Zhang</LastName>\n
            <ForeName>La</ForeName>\n
            <AffiliationInfo>\n
              <Affiliation>Department of Hepatobiliary Surgery, The First Affiliated Hospital of Chongqing Medical University, Chongqing, People\'s Republic of China.</Affiliation>\n
     </AffiliationInfo>\n
</Author>\n          '
    '''
    def match_author(self, paper_info, author):
        names = [s.lower() for s in author.split() if s]
        if len(names) == 0:
            return False
        for item in paper_info.xml_node.xpath('MedlineCitation/Article/AuthorList/Author'):
            fore_name = (item.xpath('./ForeName/text()') or [''])[0]
            last_name = (item.xpath('./LastName/text()') or [''])[0]
            initials = (item.xpath('./Initials/text()') or [''])[0]

            if fore_name != '' and last_name != '':
                if len(names) == 1:
                    if names[0] == fore_name.lower() or names[0] == last_name.lower():
                        return True
                elif len(names) == 2:
                    if names[0] == fore_name.lower() and names[1] == last_name.lower():
                        return True
                    if names[0] == last_name.lower() and names[1] == fore_name.lower():
                        return True
                else:
                    if author.lower() == fore_name.lower() + ' ' + last_name.lower():
                        return True
                    if author.lower() == last_name.lower() + ' ' + fore_name.lower():
                        return True

                if initials != '':
                    if len(names) == 2:
                        if names[0] == initials.lower() and names[1] == last_name.lower():
                            return True
                        if names[0] == last_name.lower() and names[1] == initials.lower():
                            return True
                    else:
                        if author.lower() == initials.lower() + ' ' + last_name.lower():
                            return True
                        if author.lower() == last_name.lower() + ' ' + initials.lower():
                            return True
            else:
                item_name = ''
                if fore_name != '':
                    item_name = fore_name
                elif last_name != '':
                    item_name = last_name
                elif item.find('CollectiveName') is not None:
                    item_name = (item.xpath('CollectiveName/text()') or [''])[0]

                if item_name != '':
                    pattern = r'\b{}\b'.format(re.escape(author))
                    if re.search(pattern, item_name, re.IGNORECASE):
                        return True
        return False

    def match_affiliation(self, paper_info, affiliation):
        patterns = [r'\b{}\b'.format(re.escape(n)) for n in affiliation.split() if n]
        if len(patterns) != 0:
            for i in paper_info.affiliations:
                if all(re.search(p, i, re.IGNORECASE) for p in patterns):
                    return True
        return False

    def match_journal(self, paper_info, journal):
        query = ' '.join([s for s in journal.split() if s])
        pattern = r'\b{}\b'.format(re.escape(query))
        return re.search(pattern, paper_info.journal, re.IGNORECASE)

    def match_cite(self, paper_info, cite):
        return cite in paper_info.xml_node.xpath('PubmedData/ReferenceList/Reference/ArticleIdList/ArticleId[@IdType="pubmed"]/text()')

def main():
    parser = argparse.ArgumentParser(description='Import PubMed data.')
    parser.add_argument('pubmed_dir', type=str, help='Directory containing PubMed data')
    parser.add_argument('source', type=int, help='Source of the data')
    parser.add_argument('index', type=str, nargs='?', default=None, help='Optional index value or range, eg. 2 or 3-5')
    parser.add_argument('-r', '--run', action='store_true', help='Run the import process, otherwise just test without writing anything to database')
    parser.add_argument('-m', '--mode', type=str, choices=['default', 'update-index', 'update-info'], default='default',
                        help='Mode of operation: default, update-index, update-info')
    parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')
    args = parser.parse_args()

    if args.pubmed_dir == 'help' or args.source == 'help':
        parser.print_help()
        return 0

    if not os.path.exists(args.pubmed_dir):
        print(f"ERROR: Directory not found: {args.pubmed_dir}\n")
        parser.print_help()
        return 2

    if args.source <= 0:
        print("ERROR: Source must be a positive integer\n")
        parser.print_help()
        return 1

    pubmed = PubMedXMLFile()
    if not pubmed.load(args.pubmed_dir, args.source):
        return 1

    if pubmed.pmids_to_remove:
        if not args.run:
            cnt = PubMedIndex.objects.filter(pmid__in=pubmed.pmids_to_remove).count()
            print(f"Found {cnt} PMIDs to remove from PubMedIndex")
        if args.verbose:
            print("PMIDs to remove from database:")
            for i, r in enumerate(PubMedIndex.objects.filter(pmid__in=pubmed.pmids_to_remove)):
                print(f"  {i}. PMID {r.pmid} (pk={r.pk}, source={r.source}, index={r.index}, doi={r.doi})")
        if args.run:
            cnt, _ = PubMedIndex.objects.filter(pmid__in=pubmed.pmids_to_remove).delete()
            print(f"Deleted {cnt} PMIDs from database")

    rules = []
    if args.mode == 'default':
        for rule_item in PaperTracking.objects.all():
            rules.append({
                'user': rule_item.user,
                'type': rule_item.type,
                'value': rule_item.value,
                'label': rule_item.label
                })
        print(f"Total {len(rules)} tracking rules")
    else:
        if args.verbose:
            print(f"Skip loading rules, since running in '{args.mode}' mode")

    cnt = {
        'paper': {'total': 0, 'matched': 0, 'new': 0, 'updated': 0},
        'recommendation': {'total': 0, 'new': 0, 'updated': 0},
    }
    if args.index is not None:
        m = re.match('^([0-9]+)-([0-9]+)$', args.index)
        if m:
            print(f"m = {m}")
            start, end = int(m.group(1)), int(m.group(2))
            print(f"start:{start}, end:{end}")
            if start < 1 or start > pubmed.num_articles:
                print(f"Index {start} out of range [1, {pubmed.num_articles}]")
                return 1
            if end < 1 or end > pubmed.num_articles:
                print(f"Index {end} out of range [1, {pubmed.num_articles}]")
                return 1

            pubmed.scan_rules(args.mode, rules, args.run, args.verbose, cnt, start, end)
        else:
            if not args.index.isdigit():
                print(f"Invalid index value, should be single positive integer or a range (formatted as '3-5').")
                return 1
            index = int(args.index)
            if index < 1 or index > pubmed.num_articles:
                print(f"Index {index} out of range [1, {pubmed.num_articles}]")
                return 1

            pubmed.scan_rules(args.mode, rules, args.run, args.verbose, cnt, index)
    else:
        pubmed.scan_rules(args.mode, rules, args.run, args.verbose, cnt)

    print("Total scanned {} papers ({} matched, {} new, {} updated)".format(
        cnt['paper']['total'], cnt['paper']['matched'], cnt['paper']['new'], cnt['paper']['updated']
    ))
    print("   and pushed {} recommendations ({} new, {} updated)".format(
        cnt['recommendation']['total'], cnt['recommendation']['new'], cnt['recommendation']['updated']
    ))
    return 0

if __name__ == '__main__':
    sys.exit(main())
