"""Extracts the coordinates of particular words from an HOCR document."""

import util
import sys

hocrs = sys.stdin.read()

words = sys.argv[1].split(',')

for h in hocrs.split('\n'):
    if h != '':
        coords = util.hocrWordCoordsMultiple(words, h)
        if coords is not None:
            print('%s\t%s' % coords),
