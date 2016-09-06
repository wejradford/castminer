#!/usr/bin/env python

from __future__ import print_function
import logging
import os
from utils import argparser_factory, db_factory, plot_role_counts, \
                  get_all_role_counts, FIGS

log = logging.getLogger()

p = argparser_factory()
p.add_argument('-w', '--window', default=5, type=int)
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
counts, total = get_all_role_counts(c)
log.info('Collected {} data points'.format(total))

fname = os.path.join(FIGS, 'counts.rm-{}.pdf'.format(args.window))
plot_role_counts(counts, 'counts', fname,
                 window=args.window,
                 height=args.height, width=args.width, 
                 font_size=args.font_size)
