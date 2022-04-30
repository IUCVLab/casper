import texttools

def parse_raw(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result = []
    for line in lines:
        parts = line.split('\t')
        if len(parts) == 0:
            continue
        else:
            item = {}
            item['title'] = parts[0]
            if len(parts) > 1:
                item['authors'] = parts[1]
            else:
                item['authors'] = None
            result.append(item)
    return result


def _get_relevant_preprints(title, n=100):
    api = f"http://export.arxiv.org/api/query?max_results={n}&search_query="
    import time
    import feedparser
    # 3 seconds delay is due to arxiv API requirements
    time.sleep(3)
    return feedparser.parse(api + title.replace(' ', '+'))


def _feed_to_papers(feed):
    result = []
    for e in feed["entries"]:
        id = e['id'][21:].replace('/', '_')
        page = e['id']
        year = e['published'].split('-')[0]
        pdfurl = [l['href'] for l in e['links'] if l['type'] == 'application/pdf'][0]
        title = e['title'].replace('\n', '').replace('  ', ' ')
        authors = [a['name'] for a in e.authors]
        result.append({
            'id': id,
            'url': page,
            'year': year,
            'pdfurl': pdfurl,
            'title': title,
            'authors': authors
        })
    return result


def _filter_relevant_papers(feed, item, LD=10, IOU=.01):
    import itertools
    import Levenshtein
    title = item['title'].lower()
    
    def author_set(authors):
        print("authors", authors)
        if authors is str:
            authors = authors.split()
        else:
            return []
        return set([name.lower() for name 
                    in itertools.chain(*[i.split() for i in authors]) if '.' not in name])

    query_authors = author_set(item['authors'])
    result = []
    for paper in feed:
        titles_dist = Levenshtein.distance(paper['title'].lower(), title)
        candidate_authors = author_set(paper['authors'])
        if candidate_authors and query_authors:
            iou = len(set.intersection(query_authors, candidate_authors)) / len(set.union(query_authors, candidate_authors))
        else:
            iou = 1.
        if iou >= IOU and titles_dist <= LD:
            paper['source'] = item['title']
            result.append(paper)
    return result


def collect_paper_meta(sources):
    result = []
    for paper in sources:
        feed = _get_relevant_preprints(paper['title'])
        print("Feed length:", len(feed))
        candidates = _feed_to_papers(feed)
        print("Candidate papers length:", len(candidates))
        filtered = _filter_relevant_papers(candidates, paper)
        print("Remaining candidates length:", len(filtered))
        result += filtered
    return result


def _download(url, filename):
    import requests
    import shutil
    with requests.get(url, stream=True, allow_redirects=True) as r:
        if str(r.status_code)[0] in '45':
            print(f"Error: {r.status_code}, {r.url}")
            if str(r.status_code) == '403':
                raise Exception("We are banned by arxiv :(")
        else:
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f, 1024 * 1024 * 5)


def _recognize(fromfile, tofile):
    import textract
    try:
        bin = textract.process(fromfile, method='pdfminer')
    except BaseException as e:
        print(e)
        return False
    text = str(bin, encoding="utf8")

    abbr = texttools.detect_abbreviations(text)
    print("Abbreviations:", abbr)
    text = texttools.expand_abbreviations(text, abbr)
    text = texttools.clean_text(text)

    with open(tofile, 'w') as txt:
        txt.write(text)
    return True


def download_and_parse_papers(index, folder="static/null", keepPDF=False, delay=3):
    import shutil
    import time
    import os

    fullfolder = folder
    if not os.path.exists(fullfolder):
        os.mkdir(fullfolder)
   
    for item in index:
        yearfolder = os.path.join(fullfolder, str(item['year']))
        if not os.path.exists(yearfolder):
            os.mkdir(yearfolder)
        # + '.pdf' - hack
        url = item['pdfurl'].replace('http:', 'https:') + '.pdf'
        short_file = item['id'] + '.pdf'
        filename = os.path.join(yearfolder, short_file)
        # item['pdffile'] = filename
        if os.path.exists(filename):
            # hack for the cases file was downloaded partially
            if os.path.getsize(filename) > 16 * 1024:
                continue
        time.sleep(delay)

        _download(url, filename)
        if not _recognize(filename, filename.replace('.pdf', '.txt')):
            continue

        # delete PDFs if they are not requested by the user
        if not keepPDF:
            os.remove(filename)

    # final steps -- achiving the data
    archfile = "dump"
    shutil.make_archive(folder + "/" + archfile, 'zip', folder)
    return archfile + ".zip"
