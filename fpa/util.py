"""Utilities"""

import urllib2
import subprocess
from lxml.html import parse
from StringIO import StringIO
import settings as st
from datetime import datetime

x1 = 'xmin'
y1 = 'ymin'
x2 = 'xmax'
y2 = 'ymax'


def checkDates(dates):
    """Validate a list of dates."""
    rdates = []
    for d in dates:
        accepted = False
        for f in st.accepted_date_formats:
            try:
                t = datetime.strptime(d.strip(), f)
                accepted = True
            except Exception, e:
                pass
        if accepted:
            rdates.append(d)
        else:
            rdates.append(st.NULL)
    return rdates


def checkInts(ints):
    """Validate a list of integers."""
    rints = []
    for i in ints:
        try:
            t = str(int(i.strip()))
            rints.append(t)
        except Exception, e:
            rints.append(st.NULL)
    return rints


def fuzzySplit(s, d):
    """Split on a delimiter that may be in the wrong place."""
    s = s.strip()
    try:
        if s.index(d) == 0 and ' ' in s:
            return s.replace(d, '').split(' ')[:2]
        elif s.index(d) == len(s) - len(d) and ' ' in s:
            return s.replace(d, '').split(' ')[:2]
        elif d in s:
            return s.split(d)[:2]
        elif d.strip() in s:
            return s.split(d.strip())[:2]
        else:
            return (st.NULL, st.NULL)
    except Exception, e:
        return (st.NULL, st.NULL)


def pdfToText(filename):
    """Convert a text-based PDF to HTML."""
    command = ['pdftotext', '-layout', '-nopgbrk', '-q', '-bbox']
    p = subprocess.Popen(command + [filename], stdout=subprocess.PIPE)
    p.communicate()


def dataAtHocrBboxes(bboxes, htmlpath, returnFirstWord=False):
    """Get text from HOCR within a list of bounding boxes."""
    if type(bboxes) != list:
        bboxes = [bboxes]

    data = [''] * len(bboxes)
    page = parse(htmlpath).getroot().find('.//page')
    p = 1

    for word in page.findall('word'):
        f_attribs = {}
        for a in word.attrib:
            f_attribs[a] = float(word.attrib[a])
        for i, b in enumerate(bboxes):
            if inside(b, f_attribs, p) and word.text is not None:
                data[i] = '%s%s ' % (data[i], word.text.strip())
                if returnFirstWord:
                    return data
                else:
                    break

    return data


def hocrWordCoordsMultiple(words, hocr):
    """Get any of a list of words from HOCR with bounding box."""
    page = parse(StringIO(hocr)).getroot().find('.//span')
    try:
        for w in page:
            if w.attrib['class'] == 'ocrx_word':
                childtext = ' '.join(w.xpath('.//text()'))
                childtext = childtext.strip()
                if childtext.lower() in words:
                    bbox = '\t'.join(w.attrib['title'].split(' ')[1:5])
                    return (childtext.lower(), bbox.replace(';', ''))
    except Exception, e:
        pass

    return None


def downloadBinary(url, filename):
    """Download a file."""
    req = urllib2.Request(url=url.replace(' ', '%20'))
    f = urllib2.urlopen(req)

    CHUNK = 16 * 1024
    with open(filename, 'wb') as fp:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break

            fp.write(chunk)


def inside(bbox, word, page):
    """Check to see if a word is inside a bounding box (lxml style bounding boxes)."""
    if 'page' in bbox:
        bbox_page = bbox['page']
    else:
        bbox_page = 1

    if ((word[x2] < bbox['x2']
         and word[y2] < bbox['y2']
         and word[x2] > bbox['x1']
         and word[y2] > bbox['y1'])
        or
        (word[x1] < bbox['x2']
         and word[y1] < bbox['y2']
         and word[x1] > bbox['x1']
         and word[y1] > bbox['y1'])) and \
       page == bbox_page:
        return True



