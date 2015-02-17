"""Crop an image around a box in the image closest to the size
and width/height specified.

example:
    
    Crop around the box that's 50% of the total size and
    with width/height 1.25:

        cat img.png | python cropbox.py .5 1.25 > cropped.png

"""

import numpy as np
from skimage.measure import regionprops, label
from skimage.color import rgb2gray
import sys
import StringIO
from PIL import Image

from skimage.filter import threshold_yen

minXi = 0
minYi = 1
maxXi = 2
maxYi = 3


def minX(b):
    return b[minXi]


def minY(b):
    return b[minYi]


def maxX(b):
    return b[maxXi]


def maxY(b):
    return b[maxYi]

def run_cmd(percentOfWindow, ratio):
    stdin = sys.stdin.read()
    if stdin == '\n':
        exit()

    img = Image.open(StringIO.StringIO(stdin)).convert('L')
    imgc = np.array(img)

    img = rgb2gray(imgc)

    thresh = threshold_yen(img)
    img = img > thresh


    height, width = img.shape
    imsize = width * height

    labels = label(img)

    bb = 'BoundingBox'

    regions = regionprops(labels, ['BoundingBox'])

    blobs = np.array([l[bb] for l in regions if (
        maxX(l[bb]) - minX(l[bb])) * (maxY(l[bb]) - minY(l[bb])) > 2000])

    if len(blobs) == 0:
        imout = np.uint8(imgc)
        out = Image.fromarray(imout)
        out.save(sys.stdout, format='PNG')
        exit()


    # Find closest blob to desired ratio and percent of window
    sizes = [(maxX(b) - minX(b)) * (maxY(b) - minY(b)) for b in blobs]
    percents = [s / float(imsize) for s in sizes]
    percent_diffs = [abs(percentOfWindow - p) for p in percents]

    aratios = [(maxX(b) - minX(b)) / float(maxY(b) - minY(b)) for b in blobs]
    aratio_diffs = [abs(r - ratio) for r in aratios]

    min_ratio_diff = min(aratio_diffs)
    min_percent_diff = min(percent_diffs)

    close_ratio = aratio_diffs.index(min_ratio_diff)
    close_percent = percent_diffs.index(min_percent_diff)

    if close_ratio != close_percent:
        min_ratio_score = min_ratio_diff / ratio
        min_ratio_percent_score = percent_diffs[close_ratio] / percentOfWindow

        min_percent_score = min_percent_diff / percentOfWindow
        min_percent_ratio_score = aratio_diffs[close_percent]

        if min_ratio_score * min_ratio_percent_score < min_percent_score * min_percent_ratio_score:
            b_index = close_ratio
        else:
            b_index = close_percent
    else:
        b_index = close_ratio  # They're the same

    b = blobs[b_index]

    minx = minX(b)
    miny = minY(b)
    maxx = maxX(b)
    maxy = maxY(b)

    imgc = imgc[minx:maxx, miny:maxy]

    imout = np.uint8(imgc)
    out = Image.fromarray(imout)

    out.save(sys.stdout, format='PNG')


if __name__ == '__main__':
    import clime
    clime.start(white_pattern=clime.CMD_SUFFIX, doc=__doc__, default='run', debug=False)
