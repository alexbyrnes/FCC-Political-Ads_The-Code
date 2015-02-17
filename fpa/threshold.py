"""Threshold an image.

Usage:
    
    python threshold.py gaussian | median | mean | otsu | yen | iso [blocksize (gaussian, median, and mean only)]

Example:
    
    cat input.png | python threshold.py gaussian 40 > output.png
    
    cat input.png | python threshold.py otsu > output.png

"""

import numpy as np
from skimage.color import rgb2gray, gray2rgb
import sys
import StringIO
from PIL import Image

from skimage.filter import threshold_otsu, threshold_yen, threshold_adaptive, threshold_isodata


def run_cmd(method, block_size=40):
    stdin = sys.stdin.read()
    if stdin == '\n':
        exit()

    img = Image.open(StringIO.StringIO(stdin)).convert('L')
    imgc = np.array(img)

    imggray = rgb2gray(imgc)

    if method is None or method == '':
        imgthresh = threshold_adaptive(imggray, block_size, 'gaussian', offset=10)
    elif method == 'gaussian':
        imgthresh = threshold_adaptive(imggray, block_size, 'gaussian', offset=10)
    elif method == 'median':
        imgthresh = threshold_adaptive(imggray, block_size, 'median', offset=10)
    elif method == 'mean':
        imgthresh = threshold_adaptive(imggray, block_size, 'mean', offset=10)
    elif method == 'otsu':
        thresh = threshold_otsu(imggray)
        imgthresh = imggray > thresh
    elif method == 'yen':
        thresh = threshold_yen(imggray)
        imgthresh = imggray > thresh
    elif method == 'iso':
        thresh = threshold_isodata(imggray)
        imgthresh = imggray > thresh


    rescaled = (255.0 / imgthresh.max() * (imgthresh - imgthresh.min())).astype(np.uint8)

    out = Image.fromarray(rescaled)
    out.save(sys.stdout, format='PNG')


if __name__ == '__main__':
    import clime
    clime.start(white_pattern=clime.CMD_SUFFIX, doc=__doc__, default='run', debug=False)
