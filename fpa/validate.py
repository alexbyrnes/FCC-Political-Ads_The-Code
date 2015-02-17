"""Validate (and lightly clean) various field types.  This is usually run by run_extract.py but may be run on its own with the right input file format.  Sample can be found after running run_extract.py or nosetests in the "to_validate" directory.

Example:

    cat to_validate/invoice_0.tsv | python validate.py validfile.tsv > invalidfile.tsv  


"""

from datetime import datetime
import sys
import osutil
import validation_settings as vs
import re
from itertools import product
from collections import OrderedDict
from difflib import SequenceMatcher
import settings as st



text_ix = 0
path_ix = 4
field_ix = 1 

split_ix = 4

num_cols = 12

valid_fname = sys.argv[1]


def titleCase(s):
    if len(s) <= 1:
        return s.upper()

    return ''.join([s[0].upper(), s[1:].lower()])


def copyCapitalization(model, s):

    if len(model) == 1:
        return titleCase(s)
    else:
        if model[:2].isupper():
            return s.upper()
        elif model[0].isupper() and model[1].islower():
            return titleCase(s)
        elif model[0].islower() and model[1].islower():
            return s.lower()
        else:
            return titleCase(s)


def mergeSymbols(tokens, full_text):
    keys = tokens.keys()

    regex = '(.*)'.join(keys)

    matches = re.findall('(.*)%s(.*)' % regex, full_text)[0]

    merged = []
    for i, m in enumerate(matches):
        merged.append(m)
        if i < len(keys):
            orig = tokens.keys()[i]
            fix = tokens.values()[i]
            merged.append(copyCapitalization(orig, fix))

    return ''.join(merged)


def indices(search, lst):
    return [i for i, x in enumerate(lst) if x == search]


def findValidIandSlashMatch(token):

    valid_permutations = []

    # will not return any combination of
    # i/l/I, only i for slash, l for slash etc.
    for ch in ['I', 'i', 'l']:
        lc = list(token)
        ni = lc.count(ch)
        os = indices(ch, lc)

        for permutation in product([ch, '/'], repeat=ni):
            for i, p in enumerate(permutation):

                lc[os[i]] = p

            permutation_valid = True
            wlc = ''.join(lc)
            for word in wlc.split('/'):
                if word.strip() != '' and word.lower() not in vs.common_tokens:
                    permutation_valid = False
                    break

            if permutation_valid:
                break
        if permutation_valid:
            valid_permutations.append(wlc)

    low_slash_c = None
    ret = None
    for v in valid_permutations:
        count = v.count('/')
        if low_slash_c is None or count < low_slash_c:
            low_slash_c = count
            ret = v

    return ret

# print findValidIandSlashMatch(sys.argv[1])
# exit()


def checkMostCommon(s):
    return s.lower().replace(str(st.YEAR), '').strip() in vs.most_common_tokens


def checkCommonTokens(tokens):
    for c in tokens:
        # add fixed token. In this case the match is
        # exact so the fixed is itself (default is None)
        if c.lower() in vs.common_tokens or len(c) == 1:
            tokens[c] = c


def checkCommonTokensFuzzy(tokens):
    for t in tokens.keys():
        if tokens[t] is None:
            regex_t = t.replace('l', '@')
            regex_t = regex_t.replace('i', '@')
            regex_t = regex_t.replace('@', '[li]')

            match = osutil.getStdoutFromCmd(
                '''grep -x -m 1 '%s' validation/common_tokens.tsv ''' % regex_t.lower(), shell=True)
            match = match.strip()

            if match != '':
                tokens[t] = match


def checkIandSlash(tokens):
    for t in tokens.keys():
        if tokens[t] is None:
            tokens[t] = findValidIandSlashMatch(t)


def checkKnownFields(tokens, field):

    regex_arr = []

    for t in tokens.keys():
        if tokens[t] is None:
            regex_arr.append(t)
        else:
            regex_arr.append(tokens[t])

    full_regex_arr = []

    for r in regex_arr:
        regex_t = r.replace('l', '@')
        regex_t = regex_t.replace('i', '@')
        regex_t = regex_t.replace('@', '[li]')
        full_regex_arr.append(regex_t)

    greps = 'cat validation/validate_%s.tsv' % field
    for r in full_regex_arr:
        greps += ''' | grep -w '%s' ''' % r.lower()

    match = osutil.getStdoutFromCmd(greps, shell=True)
    match = match.strip()

    if match != '':
        for i, r in enumerate(full_regex_arr):
            matches = re.findall(r.lower(), match)
            tokens[tokens.items()[i][0]] = matches[0]


def checkUrl(tokens, file_id):

    regex_arr = []

    for t in tokens.keys():
        if tokens[t] is None:
            regex_arr.append(t)
        else:
            regex_arr.append(None)  # Placeholder so index stays the same

    full_regex_arr = []

    for r in regex_arr:
        if r is None:
            full_regex_arr.append(None)
        else:
            regex_t = r.replace('l', '@')
            regex_t = regex_t.replace('i', '@')
            regex_t = regex_t.replace('@', '[li]')
            # replace slashes as well
            # may become obsolete TODO
            regex_t = regex_t.replace('/', '/ && /')
            full_regex_arr.append(regex_t)

    awk_tokens = '/%s/' % '/ && /'.join(
        [r for r in full_regex_arr if r is not None])
    match = osutil.getStdoutFromCmd(
        '''awk '/%s/ && %s' validation/validate_url.tsv ''' % (file_id, awk_tokens.lower()), shell=True)
    match = match.strip()

    if match != '':
        for i, r in enumerate(full_regex_arr):
            if r is not None:
                matches = re.findall(r.lower(), match)
                tokens[tokens.items()[i][0]] = matches[0]


def deOCRDate(d):
    d = list(d)
    if len(d) == 8:
        if d[2] in ['1', ' ']:
            d[2] = '/'
        if d[5] in ['1', ' ']:
            d[5] = '/'
    return ''.join(d)


def validDate(d):
    try:
        date = datetime.strptime(d, '%m/%d/%y')
    except Exception, e:
        return None
    return date


def split_callsign(s):

    # return s.split('_')[0].split('-')[0].split(' ')[0].split('/')[-1]
    return s.split('_')[0].split('-')[0].split('/')[-1]


def write_valid(cols):
    valid_file = open(valid_fname, 'a')
    cols[path_ix] = cols[path_ix].split('/')[-1].split('.')[0]
    valid_file.write('\t'.join(cols[:split_ix + 1]) + '\n')
    valid_file.close()


def invalidate(cols):
    print '\t'.join(cols[split_ix:])


def validate_date_range(cols, clean_text, delimiter, col_names=('from', 'to')):
    dates = clean_text.split(delimiter)
    dates = [deOCRDate(s.strip()) for s in dates]
    dates_valid = True

    if len(dates) != 2:
        dates_valid = False
    else:
        d1 = validDate(dates[0])
        d2 = validDate(dates[1])
        if d1 is None or d2 is None or d2 < d1 or d1.year != st.YEAR or d2.year != st.YEAR:
            dates_valid = False

    if dates_valid:
        cols[text_ix] = dates[0]
        cols[field_ix] = col_names[0]
        write_valid(cols)

        cols[text_ix] = dates[1]
        cols[field_ix] = col_names[1]
        write_valid(cols)
    else:
        invalidate(cols)


def validate_station(cols, clean_text):
    id_station = split_callsign(cols[path_ix])
    text = split_callsign(clean_text)

    if id_station == text or id_station.replace('-TV', '') == text or (id_station, text) in vs.station_aliases:
        cols[text_ix] = text
        write_valid(cols)
    else:
        invalidate(cols)


def validate_fixed(cols, clean_text, values):
    if clean_text in values:
        cols[text_ix] = clean_text
        write_valid(cols)
    else:
        invalidate(cols)


def validate_pattern(cols, clean_text, common, patterns):
    if clean_text in common:
        write_valid(cols)
        return
    else:
        for p in patterns:
            m = re.search(p, clean_text)
            if m:
                cols[text_ix] = m.group(0)
                write_valid(cols)
                return

    invalidate(cols)


def validate_product_advertiser(cols, clean_text):
    if checkMostCommon(clean_text):
        cols[text_ix] = clean_text
        write_valid(cols)
        return

    # OrderedDict with cleaned value or None for fail
    tokens_arr = re.findall('[^\W\d]+', clean_text)
    tokens = OrderedDict([(t, None) for t in tokens_arr])

    checkCommonTokens(tokens)

    if None not in tokens.values():
        cols[text_ix] = mergeSymbols(tokens, clean_text)
        write_valid(cols)
        return

    checkCommonTokensFuzzy(tokens)

    if None not in tokens.values():
        cols[text_ix] = mergeSymbols(tokens, clean_text)
        write_valid(cols)
        return

    # filter tokens that can be made valid by replacing
    # one or more I's with slashes.
    checkIandSlash(tokens)

    if None not in tokens.values():
        cols[text_ix] = mergeSymbols(tokens, clean_text)
        write_valid(cols)
        return

    # grep known fields (order matters)
    checkKnownFields(tokens, field)

    if None not in tokens.values():
        cols[text_ix] = mergeSymbols(tokens, clean_text)
        write_valid(cols)
        return

    docid = cols[path_ix].split('/')[-1].split('.')[0]
    checkUrl(tokens, docid)

    if None not in tokens.values():
        cols[text_ix] = mergeSymbols(tokens, clean_text)
        write_valid(cols)
        return

    invalidate(cols)


def validate_advertiser_address(cols, clean_text):
    clean_text_tokens = re.findall('[\w]+', clean_text.lower())

    regex = '.*'.join(clean_text_tokens)

    status = osutil.getExitStatusFromCmd(
        '''grep -q '%s' validation/validate_%s.tsv ''' % (regex, field), shell=True)

    if status == 0:
        cols[text_ix] = clean_text
        write_valid(cols)
        return
    else:
        invalidate(cols)


def validate_special_handling(cols, clean_text, custom_adds=None):
    if clean_text == '':
        write_valid(cols)
        return

    tokens_arr = re.findall('[^\W\d]+', clean_text)
    tokens = OrderedDict([(t, None) for t in tokens_arr])

    checkCommonTokens(tokens)

    if custom_adds is not None:
        for t in tokens:
            if t in custom_adds:
                tokens[t] = t

    if None not in tokens.values():
        cols[text_ix] = mergeSymbols(tokens, clean_text)
        write_valid(cols)
        return
    else:
        invalidate(cols)


def validate_doctype(cols, clean_text):
    for tp in ['invoice', 'order', 'contract']:
        if tp in clean_text.lower():
            cols[text_ix] = tp
            write_valid(cols)
            return

    invalidate(cols)


def validate_agreement(cols, clean_text):

    matches = re.findall('[A-Z]+', clean_text)
    uppers = ' '.join(matches)
    uppers = removeSinglesAndSymbols(uppers)
    for t in vs.agreement_templates:
        if similarity(t[0], uppers) > t[1]:
            cols[text_ix] = t[2]
            write_valid(cols)
            return

    invalidate(cols)


def reject_blank(cols, clean_text):
    if clean_text == '':
        invalidate(cols)


def removeSinglesAndSymbols(s):
    matches = re.findall('[\w]+', s)
    ret = []
    for m in matches:
        if len(m) > 1:
            ret.append(m)
    return ' '.join(ret)


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

i = 1

for line in sys.stdin.readlines():

    cols = line.strip().split('\t')

    if len(cols) == num_cols - 1:
        cols.insert(0, '')

    if len(cols) == num_cols:

        field = cols[1]

        clean_text = cols[text_ix].strip()

        if field in ['contract_dates', 'invoice_period', 'flight_dates']:
            col_name = field.split('_')[0]
            validate_date_range(cols, clean_text, delimiter='-', col_names=(col_name + '_from', col_name + '_to'))
        elif field == 'station':
            validate_station(cols, clean_text)
        elif field == 'billing_calendar':
            validate_fixed(cols, clean_text, vs.billing_calendar)
        elif field == 'billing_cycle':
            validate_fixed(cols, clean_text, vs.billing_cycle)
        elif field == 'demographic':
            validate_pattern(cols, clean_text, vs.common_demographics, vs.demographic_patterns)
        elif field in ['product', 'advertiser']:
            validate_product_advertiser(cols, clean_text)
        elif field == 'advertiser_address':
            validate_advertiser_address(cols, clean_text)
        elif field == 'special_handling':
            validate_special_handling(
                cols, clean_text, custom_adds=vs.special_handling)
        elif field in ['contract_revision']:
            # no way to validate yet
            cols[text_ix] = clean_text
            write_valid(cols)
        elif field == 'doctype':
            if clean_text == '':
                continue
            validate_doctype(cols, clean_text)
        elif field == 'agreement':
            if clean_text == '':
                continue
            validate_agreement(cols, clean_text)
        else:
            # unknown field
            cols[text_ix] = clean_text
            write_valid(cols)

    else:
        invalidate(cols)
