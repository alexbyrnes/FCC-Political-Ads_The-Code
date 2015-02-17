"""Avoid broken pipes from applications with no output"""

import sys

lines = sys.stdin.readlines()
line = ' '.join(lines)
if line.strip() == '':
    print
else:
    print line,
