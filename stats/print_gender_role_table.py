#!/usr/bin/env python

from __future__ import print_function
import itertools
from utils import argparser_factory, db_factory, DEFAULT_MEDIUM, MEDIA


def fetch_column(c, gender, limit=20, medium=DEFAULT_MEDIUM, normalise=True):
    if args.normalise:
        c.execute('''
        SELECT CAST(SUM(count * {}) AS INT) 
        FROM parts 
        WHERE {}'''.format(order, MEDIA[medium]))
        (total,) = c.fetchone()
        total = float(total)
    q = '''
    SELECT name, CAST(SUM(count * {}) AS INT) AS total
    FROM parts
    WHERE {}
    GROUP BY name
    ORDER BY total DESC
    LIMIT ?'''.format(order, MEDIA[medium])
    c.execute(q, (limit,))
    column = []
    column.append('{}\t{}'.format(medium or '', order))
    if args.normalise:
        data = ['{}\t{:.4f}'.format(name, count / total) for name, count in c.fetchall()]
    else:
        data = ['{}\t{}'.format(name, count) for name, count in c.fetchall()]
    column.extend(data)
    return column

p = argparser_factory()
p.add_argument('--limit', type=int, default=20)
p.add_argument('--by-media', default=False, action='store_true')
p.add_argument('--normalise', default=False, action='store_true')
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
columns = []

if not args.by_media:
    for order in ('female', 'male'):
        columns.append(fetch_column(c, order, limit=args.limit, medium=DEFAULT_MEDIUM, normalise=args.normalise))
else:
    for medium in ('FILM', 'TV'):
        for order in ('female', 'male'):
            columns.append(fetch_column(c, order, limit=args.limit, medium=medium, normalise=args.normalise))

for cols in itertools.izip(*columns):
    print('\t'.join(cols))
