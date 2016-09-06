#!/usr/bin/env python

from __future__ import print_function
import logging
import os
from utils import argparser_factory, db_factory, LATEST_YEAR, np, \
                  plt, pd, sns, FIGS, MEDIA, plot_rolling_hellinger
from scipy.linalg import norm

log = logging.getLogger()

SQRT2 = np.sqrt(2)
def hellinger(a, b):
    return norm(np.sqrt(a) - np.sqrt(b)) / SQRT2

def get_dist(t, name_index, cursor, medium, gender=None):
    if gender is None:
        q = '''
        SELECT name, SUM(count)
        FROM parts
        WHERE year = ?
        AND {}
        GROUP BY name'''.format(MEDIA[medium])
    else:
        q = '''
        SELECT name, SUM({} * count)
        FROM parts
        WHERE year = ?
        AND {}
        GROUP BY name'''.format(gender, MEDIA[medium])
    cursor.execute(q, (t,))
    d = np.zeros(len(name_index))
    for name, count in cursor.fetchall():
        d[name_index[name]] = count
    z = np.sum(d)
    if z == 0:
        return None, None
    d /= z
    log.info('{} -> {}:{} (n={})'.format(t, d.max(), d.min(), z))
    return d, z

p = argparser_factory()
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()

log.info('Building name index')
c.execute('SELECT DISTINCT name FROM parts')
name_index = {name: i for i, (name,) in enumerate(c.fetchall())}
log.info('Loaded {} names'.format(len(name_index)))

log.info('Fetching time-slices.')
ds = {}
last_t1_d_z = None
gender = None
earliest_year = 1960
for m in ('FILM', 'TV'):
    for t in xrange(earliest_year, LATEST_YEAR):
        t1 = t + 1
        if last_t1_d_z is not None:
            t_d, t_z = last_t1_d_z
        else:
            t_d, t_z = get_dist(t, name_index, c, m, gender)
        t1_d, t1_z = get_dist(t1, name_index, c, m, gender)
        if t_d is None or t1_d is None:
            d = 0
        else:
            d = hellinger(t_d, t1_d)
        
        log.debug('Window {}-{}\td {:.3f}'.format(t, t1, d))
        last_t1_d_z = (t1_d, t1_z)
        ds.setdefault(t, {})[m] = d
        ds.setdefault(t, {})[m + ' count'] = t_z
data = []
index = []
for y, d in sorted(ds.iteritems()):
    d['year'] = y
    data.append(d)
    index.append(y)
counts = pd.rolling_mean(pd.DataFrame(data, index=index, columns=['TV count', 'FILM count']), 5)
diffs = pd.rolling_mean(pd.DataFrame(data, index=index, columns=['TV', 'FILM']), 5)

#tv_corr = pd.rolling_corr(counts['TV count'], diffs['TV'], window=5) + 1
#film_corr = pd.rolling_corr(counts['FILM count'], diffs['FILM'], window=5) + 1

fname = os.path.join(FIGS, 'rolling-hellinger.pdf')
plot_rolling_hellinger(diffs, fname, earliest_year, height=args.height, width=args.width,
                       font_size=args.font_size)
