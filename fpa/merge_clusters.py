"""Finds equivalent strings with abbreviations.  Will find the 
matching string with the highest "score."  Scores should be in 
the second column of the input file.


example: 
    
    python merge_clusters.py clusters.tsv


Example input (tab delimited):

Democratic Governors Association	25
Democratic Gov Assoc	2
Comm for Employment Oppty OH	62
Cmte for Empl Oppty FL	6
Committee for Employment Opportunity	85
Dem Governors Assn	8

Output:
    
Democratic Gov Assoc	Democratic Governors Association
Comm for Employment Oppty OH	Committee for Employment Opportunity
Cmte for Empl Oppty FL	Committee for Employment Opportunity
Dem Governors Assn	Democratic Governors Association

"""

from abbreviations import abbrs
import validation_settings as vs
import re
import sys


skip_words = vs.states_abbr | vs.states | vs.states_ap_abbr | vs.months | vs.days


def hasCommon(a, b):
    return len(set(a) & set(b)) > 0


def getCommon(a, b):
    return list(set(a) & set(b))[0]


def canSkip(s, abbrs, skip_words):
    return s in skip_words and s not in abbrs


def canBePacked(s, target):
    s_tokens = re.findall('[^\W\d]+', s.lower())
    t_tokens = re.findall('[^\W\d]+', target.lower())

    rep = set()

    for st in s_tokens:
        if st in t_tokens:
            rep.update([st])
            continue

        trunc = [t[:len(st)] for t in t_tokens]
        if len(st) > 2 and st in trunc:
            rep.update([t_tokens[trunc.index(st)]])
            continue

        if canSkip(st, abbrs, skip_words) or (st in abbrs and '' in abbrs[st]) or len(st) == 1:
            if st in t_tokens:
                rep.update([t_tokens[t_tokens.index(st)]])
            continue

        if st in abbrs and hasCommon(abbrs[st], t_tokens):
            c = getCommon(abbrs[st], t_tokens)
            rep.update([t_tokens[t_tokens.index(c)]])
        else:
            return False

    if rep == set(t_tokens):
        return True

    return False


def highestMatch(fixes, counts):
    sort = sorted([(f, counts[f]) for f in fixes], key=lambda x: x[1])
    return sort[0][0]

def run_cmd(groupsfile):
    groups = list(open(groupsfile, 'r'))

    split_groups = [(g.split('\t')[0].strip(), g.split('\t')[1].strip()) for g in groups]

    counts = {}

    for g in split_groups:
        if g[0] not in counts or g[1] > counts[g[0]]:
            counts[g[0].strip()] = int(g[1])


    for lb in groups:
        if 'no on' in lb.lower() or 'yes on' in lb.lower():
            continue

        poss_f = []

        (b, b_count) = lb.strip('\n').split('\t')
        b = b.strip()
        fixed = [g for g in groups if int(g.split('\t')[1]) > counts[b]]
        for lf in fixed:
            (f, f_count) = lf.strip('\n').split('\t')
            f = f.strip()
            if canBePacked(b.lower(), f.lower()):
                poss_f.append(f)
        if len(poss_f) > 0:
            high = highestMatch(poss_f, counts)
            print b + '\t' + high


if __name__ == '__main__':
    import clime
    clime.start(white_pattern=clime.CMD_SUFFIX, doc=__doc__, default='run', debug=False)
