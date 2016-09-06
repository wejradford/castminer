#!/usr/bin/env python
from __future__ import print_function
from collections import Counter
import re
import sys

COMPANY = re.compile('^(.*)\[(.*)\]$')
looking = False
stats = Counter()
for line in sys.stdin:
    line = line.rstrip().decode('iso_8859-1')
    if line == '=========================':
        looking = True
    elif not looking:
        continue
    else:
        bits = line.split('\t')
        title = bits[0]
        name = lang = None
        for i in reversed(bits):
            m = COMPANY.match(i)
            if m is not None:
                name, lang = COMPANY.match(i).groups()
                break
        if lang is None:
            #print(u'Unable to extract from "{}"'.format(line), file=sys.stderr)
            stats['failure'] += 1
        else:
            print(u'{}\t{}'.format(title, lang).encode('utf8'))
            stats['ok'] += 1
total = float(stats['ok'] + stats['failure'])
print('{:.1f}% coverage of {}'.format(100*stats['ok'] / total, int(total)), file=sys.stderr)
