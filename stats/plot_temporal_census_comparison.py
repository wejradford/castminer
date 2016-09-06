#!/usr/bin/env python

from __future__ import print_function
import logging
import pprint
from utils import argparser_factory, db_factory, read_imdb_census_mapping, \
            read_census_data, get_gender_roles_for_year, np, z_proportion, \
            plot_census_comparison, get_census_comparisons, FONT_SIZE

log = logging.getLogger()

p = argparser_factory()
p.add_argument('--mapping', required=True)
p.add_argument('--census', required=True)
p.add_argument('--medium', default=None)
p.add_argument('--year', default=None, type=int)
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
all_plot_data = get_census_comparisons(args.mapping, args.census, c, 
                                       focus_year=args.year, medium=args.medium)
for year, plot_data in sorted(all_plot_data.iteritems()):
    if not plot_data:
        log.error('No plot data for {}'.format(year))
    else:
        plot_census_comparison(plot_data, year, args.medium, font_size=args.font_size)
