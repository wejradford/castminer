#!/usr/bin/env python

from __future__ import print_function
import logging
from utils import argparser_factory, db_factory, plot_gender_counts_pf, get_gender_counts_for_year

log = logging.getLogger()

p = argparser_factory()
p.add_argument('-w', '--window', default=5, type=int)
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
counts = get_gender_counts_for_year(c)
plot_gender_counts_pf(counts, 'gender-counts', 
                      window=args.window,
                      height=args.height, width=args.width,
                      font_size=args.font_size)

