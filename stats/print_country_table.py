#!/usr/bin/env python

from __future__ import print_function
from utils import argparser_factory, db_factory

p = argparser_factory()
p.add_argument('--limit', type=int, default=20)
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()

q = 'SELECT SUM(count) FROM parts'
c.execute(q)
(total,) = c.fetchone()
total = float(total)

c.execute('''
SELECT country, SUM(count) 
FROM parts 
GROUP BY country 
ORDER BY SUM(count) DESC
LIMIT ?''', (args.limit,))
for country, count in c.fetchall():
    print('{}\t{}\t{:.1f}'.format(country, count, 100*float(count / total)))
