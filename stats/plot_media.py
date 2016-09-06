#!/usr/bin/env python

from __future__ import print_function
from utils import argparser_factory, db_factory, \
                  plot_gender_counts_pf_by_medium, \
                  MEDIA

p = argparser_factory()
args = p.parse_args()
db = db_factory(args.db)
c = db.cursor()

counts = {}
p_females = {}
earliest_year = 1960
for medium in ['FILM', 'TV']:
    c.execute('''
    SELECT year, SUM(count), SUM(count * female) / SUM(count) 
    FROM parts
    WHERE {}
    AND year > ?
    GROUP BY year'''.format(MEDIA[medium]), (earliest_year,))
    for year, count, p_female in c.fetchall():
        counts.setdefault(medium, {})[year] = count
        p_females.setdefault(medium, {})[year] = p_female

plot_gender_counts_pf_by_medium(counts, p_females, 'media', 
                                height=args.height, 
                                width=args.width, 
                                font_size=args.font_size,
                                earliest_year=earliest_year)
