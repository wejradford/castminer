#!/usr/bin/env python
from __future__ import print_function
from collections import Counter
import operator
import sys
import itertools

def iter_rows(f):
    for line in f:
        name, role, year, gender, rank, medium, voice, country = line.rstrip().split('\t')
        yield name, role, year, gender, rank, medium, voice, country

# Sorted by: year, medium, role, name.
seen = set()
for year, year_records in itertools.groupby(iter_rows(sys.stdin), operator.itemgetter(2)):
    for medium, medium_records in itertools.groupby(year_records, operator.itemgetter(5)):
        for country, country_records in itertools.groupby(medium_records, operator.itemgetter(7)):
            for role, records in itertools.groupby(country_records, operator.itemgetter(1)):
                key = (year, medium, country, role)
                assert not key in seen, 'Already seen {}, check sorting!'.format(key)
                seen.add(key)
                counts = Counter(g for _, _, _, g, _, _, _, _ in records)
                total = sum(counts.values())
                dist = {g: c / float(total) for g, c in counts.items()}
                print('{}\t{}\t{}\t{}\t{}\t{:.5f}\t{:.5f}'.format(
                        year, role, medium, country, 
                        total, dist.get('F', 0), dist.get('M', 0)))
