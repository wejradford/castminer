#!/usr/bin/env python

from __future__ import print_function
import itertools
import logging
from utils import argparser_factory, db_factory, DECADES,\
                  MEDIA, DEFAULT_MEDIUM

p = argparser_factory()
p.add_argument('--medium', default=DEFAULT_MEDIUM)
p.add_argument('--emerging', default=False, action='store_true')
p.add_argument('--limit', type=int, default=20)
p.add_argument('--top', type=int, default=50)
p.add_argument('--reversed', default=False, action='store_true')
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
header = []
columns = []
for start, stop in DECADES:
    label = '{}--{}'.format(start, stop)
    logging.info(label)
    q = '''
    SELECT name, SUM(count) AS TOTAL
    FROM parts
    WHERE {}
    AND year > ?
    AND year < ?
    GROUP BY name
    ORDER BY total DESC
    LIMIT ?'''.format(MEDIA[args.medium])
    c.execute(q, (start, stop, args.limit*10))
    column = []
    column.append((label, 'c'))
    column.extend(list(c.fetchall()))
    columns.append(column)

if args.emerging:
    seen = set()
    filtered = []
    if args.reversed:
        filter_order = list(reversed(columns[:]))
    else:
        filter_order = columns[:]
    for c in filter_order:
        filtered.append(c[:1] + [(name, count) for name, count in c[1:] if not name in seen])
        top_n = [i[0] for i in c[1:args.top + 1]]
        logging.info('{}\tfiltering by top {}'.format(c[0][0], len(top_n)))
        seen.update(top_n)

    if args.reversed:
        filtered = list(reversed(filtered))
else:
    filtered = columns

for i, row in enumerate(itertools.izip_longest(*filtered, fillvalue=('', ''))):
    print('\t'.join(u'{}\t{}'.format(*c) for c in row).encode('utf8'))
    if i == args.limit:
        break
