#!/usr/bin/env python

from __future__ import print_function
from utils import argparser_factory, db_factory, pd, np, MEDIA, DEFAULT_MEDIUM

p = argparser_factory()
p.add_argument('--limit', default=20, type=int)
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
c.execute('''
SELECT name, year, SUM(count) AS total, SUM(count*female) AS ftotal, SUM(count*female) / SUM(count) AS pf
FROM parts
WHERE {}
GROUP BY name, year
HAVING SUM(count) > ?
ORDER BY pf DESC'''.format(MEDIA[DEFAULT_MEDIUM], (args.limit,)))

df = pd.DataFrame(c.fetchall(), columns=['name', 'total', 'ftotal', 'pf'])
BANDS = [
    (0, 0.2),
    (0.2, 0.4),
    (0.4, 0.6),
    (0.6, 0.8),
    (0.8, 1.0),
]
for start, end in BANDS:
    with open('tbl/popular-gendered-roles-{}-{}.txt'.format(start, end), 'w') as f:
        for _, row in df.query('(pf > {}) & (pf < {})'.format(start, end)).sort('total').iterrows():
            print(u'{}\t{}\t{}\t{:.3f}'.format(row['name'], row['total'], int(row['ftotal']), row['pf']).encode('utf8'), file=f)
