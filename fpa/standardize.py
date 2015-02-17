"""Standardize data.  Make addresses and titlecase consistent
for string clustering.

example:
    python standardize.py inputfile.tsv validate_address -c 3

options:
    -c <int>, --column=<int>  Column in the file with the data to be standardized.
    -m <str>, --method=<str>  Which standardization to use: standardize_address, validate_address (with geocode), titlecase.
    --header  Input file has a header line.
"""

import sys
from titlecase import titlecase
import validation_settings as vs
import re
from address import AddressParser
from pygeocoder import Geocoder

exceptions = ['yes on', 'no on', ' 4 ']

deletions = [(r' (?i)suite [#]*[ ]*[0-9]*', ''),
             (r' (?i)ste[\.]* [#]*[ ]*[0-9]* ', ' ')]


def removeExtraAddressElements(s):
    for d in deletions:
        s = re.sub(d[0], d[1], s)

    return s


def getFirstNumberIndex(s):

    for i, c in enumerate(s):
        if c.isdigit():
            return i

    return None


def validateAddress(s):
    try:
        first_number = getFirstNumberIndex(s)
        name = s[:first_number]
        address = s[first_number:]
        geo_address = Geocoder.geocode(address)
        if geo_address.valid_address:
            return name + geo_address.formatted_address
    except Exception, e:
        return None
    return None


def fixTitlecase(s):
    has_exception = False
    for exception in exceptions:
        if exception in s.lower():
            has_exception = True

    if not has_exception:
        s = removeSymbols(s)

    return titlecase(s.upper(), callback=abbreviations)


def abbreviations(word, **kwargs):
    if word.upper() in vs.abbreviations or word.lower() in vs.states_abbr:
        return word.upper()


def mergeSlashes(tokens, full_text):
    # Note: This does not use lower and
    # then copy capitalization from original.

    regex = '(.*)'.join(tokens)

    matches = re.findall('(.*)%s(.*)' % regex, full_text)[0]

    merged = []
    for i, m in enumerate(matches):

        if m == '/' and i != 0:
            merged.append(m)
        else:
            merged.append(' ')

        if i < len(tokens):
            merged.append(tokens[i])

    return ''.join(merged).strip()


def removeSymbols(s):

    tokens = re.findall('[^\W\d]+', s)

    if tokens is None:
        return ''

    no_symbols = ''.join(tokens)
    if len(no_symbols) <= 2 and no_symbols.upper() not in vs.abbreviations:
        if no_symbols != '':
            return '<discard %s>' % no_symbols
        else:
            return ''
    else:
        return mergeSlashes(tokens, s)


def removeExtraSpaces(s):
    return ' '.join(s.split())


def standardizeAddress(s, ap):
    first_number = getFirstNumberIndex(s)
    name = s[:first_number]
    address = s[first_number:]

    clean_address = ap.parse_address(address).full_address()

    clean_address = clean_address.replace('(', '').replace(')', '')

    return name.strip() + ' ' + clean_address


DEBUG = True

def run_cmd(inputfile, method, column=None, header=False):
    """-c <int>, --column=<int>
    -m <str>, --method=<str>
    """
    
    f = open(inputfile, 'r')
    edit_ix = int(column)


    if header:
        header_line = f.readline()
    firstline = True

    ap = AddressParser()

    for l in f:

        cols = l.split('\t')
        if firstline and header:
            print header_line.strip()
            firstline = False

        try:
            entity = cols[edit_ix].strip()
            if method == 'standardize_address':
                entity = standardizeAddress(entity, ap)
            elif method == 'titlecase':
                entity = fixTitlecase(entity)
            elif method == 'validate_address':

                entity = removeExtraAddressElements(entity)

                ret = validateAddress(entity)

                if ret is None:
                    entity = entity + '\tINVALID'
                else:
                    entity = ret + '\tVALID'

            else:
                print('Error: method not found')
                exit()

            cols[edit_ix] = removeExtraSpaces(entity)

            ledited = '\t'.join(cols)
            print ledited.strip()
        except Exception, e:
            if DEBUG:
                raise e
            print '\t'.join(cols).strip()


if __name__ == '__main__':
    import clime
    clime.start(white_pattern=clime.CMD_SUFFIX, doc=__doc__, default='run', debug=False)
