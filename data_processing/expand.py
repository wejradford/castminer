#!/usr/bin/env python
import re
import sys

SPLITS = re.compile(r'[/\\]| - ')
SELVES = re.compile('himself|herself|themselves', re.I)
PARENS = re.compile('\(.*\)')
ORDINAL_PREFIX = re.compile('^(First|Second|Third|Fourth|Fifth|1st|2nd|3rd|4th|5th)', re.I)
ORDINAL_SUFFIX = re.compile('\(?({})\)?$'.format('|'.join('#?{}'.format(i) for i in range(20))), re.I)

for l in sys.stdin:
    name, role, year, gender, rank, medium, voice, country = l.rstrip().split('\t')
    if role.lower() == 'n/a':
        continue
    for r in SPLITS.split(role):
        if SELVES.search(r) or not r.strip():
            continue
        r = ORDINAL_SUFFIX.sub('', ORDINAL_PREFIX.sub('', PARENS.sub('', r).strip())).strip()
        if not r.strip():
            continue
        print '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(name, r.lower(), year, gender, rank, medium, voice, country)
