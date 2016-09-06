#!/usr/bin/env python

from __future__ import print_function
from utils import argparser_factory, db_factory, plot_gender_counts_pf, \
                  get_gender_counts_for_year, EARLIEST_YEAR


p = argparser_factory()
p.add_argument('roles', nargs='+')
p.add_argument('--by-media', default=False, action='store_true')
p.add_argument('--earliest-year', default=EARLIEST_YEAR, type=int)
p.add_argument('-w', '--window', default=5, type=int)
args = p.parse_args()


db = db_factory(args.db)
c = db.cursor()
for role in args.roles:
    if args.by_media:
        c.execute('''
        SELECT year, medium, SUM(count), SUM(count * female) / SUM(count) 
        FROM parts
        WHERE name LIKE ?
        GROUP BY year, medium;''', ('%{}%'.format(role),))
        counts = {}
        p_females = {}
        for year, medium, count, p_female in c.fetchall():
            if medium not in {'FILM', 'TV', 'VIDEO'}:
                continue
            if medium in {'FILM', 'VIDEO'}:
                medium = 'FILM'
            counts.setdefault(medium, {})[year] = count
            p_females.setdefault(medium, {})[year] = p_female

        plot_gender_counts_pf(counts, p_females, role + '_media')
    else:
        counts = get_gender_counts_for_year(c, role)
        plot_gender_counts_pf(counts, role, window=args.window, 
                              earliest_year=args.earliest_year,
                              height=args.height, width=args.width, 
                              font_size=args.font_size)
