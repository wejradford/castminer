#!/usr/bin/env python

from __future__ import print_function
import logging
import os
import pprint
from utils import argparser_factory, db_factory, read_imdb_census_mapping, \
            read_census_data, get_gender_roles_for_year, np, z_proportion, \
            plot_census_comparison, get_census_comparisons, pd, plt, sns, FIGS, \
            DEFAULT_MEDIUM, FONT_SIZE, plot_census_comparison_line

sns.set_style('white', {'xtick.major.size': 0})
log = logging.getLogger()

p = argparser_factory()
p.add_argument('roles', nargs='+')
p.add_argument('--mapping', required=True)
p.add_argument('--census', required=True)
p.add_argument('--medium', default=DEFAULT_MEDIUM)
p.add_argument('--year', default=None, type=int)
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
all_plot_data = get_census_comparisons(args.mapping, args.census, c, 
                                       focus_year=args.year, medium=args.medium)
for role in args.roles:
    print(role)
    data = []
    years = []
    longest_stretch = 0
    stretch = 0
    annotations = []
    for year in xrange(2003, 2015):
        # Yuck.
        by_role = {i['role']: i for i in all_plot_data.get(year, [])}
        years.append(year)
        if not role in by_role:
            longest_stretch = max(stretch, longest_stretch)
            stretch = 0
            data.append({})
        else:
            r = by_role[role]
            sig = r['z'] is not None and abs(r['z']) > 1.96
            if sig:
                annotations.append((year, r['IMDb']))
                annotations.append((year, r['Census']))
            data.append({'IMDb': r['IMDb'], 'Census': r['Census']})
            stretch += 1
    longest_stretch = max(stretch, longest_stretch)
    df = pd.DataFrame(data, index=years)
    if df.empty or longest_stretch <= 3:
        continue
    print(df)
    fname = os.path.join(FIGS, 'IMDbVsCensus_{}_line.pdf'.format(role))
    plot_census_comparison_line(df, annotations, fname=fname, 
                                width=args.width, height=args.height,
                                font_size=args.font_size)
