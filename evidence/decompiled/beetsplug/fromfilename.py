# Source Generated with Decompyle++
# File: fromfilename.pyc (Python 3.9)

'''If the title is empty, try to extract track and title from the
filename.
'''
from beets import plugins
from beets.util import displayable_path
import os
import re
PATTERNS = [
    '^(?P<artist>.+)[\\-_](?P<title>.+)[\\-_](?P<tag>.*)$',
    '^(?P<track>\\d+)[\\s.\\-_]+(?P<artist>.+)[\\-_](?P<title>.+)[\\-_](?P<tag>.*)$',
    '^(?P<artist>.+)[\\-_](?P<title>.+)$',
    '^(?P<track>\\d+)[\\s.\\-_]+(?P<artist>.+)[\\-_](?P<title>.+)$',
    '^(?P<title>.+)$',
    '^(?P<track>\\d+)[\\s.\\-_]+(?P<title>.+)$',
    '^(?P<track>\\d+)\\s+(?P<title>.+)$',
    '^(?P<title>.+) by (?P<artist>.+)$',
    '^(?P<track>\\d+).*$']
BAD_TITLE_PATTERNS = [
    '^$']

def equal(seq):
    '''Determine whether a sequence holds identical elements.
    '''
    return len(set(seq)) <= 1


def equal_fields(matchdict, field):
    '''Do all items in `matchdict`, whose values are dictionaries, have
    the same value for `field`? (If they do, the field is probably not
    the title.)
    '''
    return None((lambda .0 = None: for m in .0:
m[field])(matchdict.values()))


def all_matches(names, pattern):
    '''If all the filenames in the item/filename mapping match the
    pattern, return a dictionary mapping the items to dictionaries
    giving the value for each named subpattern in the match. Otherwise,
    return None.
    '''
    matches = { }
    for item, name in names.items():
        m = re.match(pattern, name, re.IGNORECASE)
        if m and m.groupdict():
            matches[item] = m.groupdict()
            continue
        return None
    return matches


def bad_title(title):
    '''Determine whether a given title is "bad" (empty or otherwise
    meaningless) and in need of replacement.
    '''
    for pat in BAD_TITLE_PATTERNS:
        if re.match(pat, title, re.IGNORECASE):
            return True
        return False


def apply_matches(d):
