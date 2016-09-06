#!/usr/bin/env python

from __future__ import print_function
import logging
from utils import argparser_factory, db_factory, EARLIEST_YEAR, \
                  LATEST_YEAR, np, plt, pd, sns, MEDIA
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
    cursor.execute(q, (t, medium))
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
for m in ('FILM', 'TV'):
    for t in xrange(EARLIEST_YEAR, LATEST_YEAR+1):
        t_m_d, t_m_z = get_dist(t, name_index, c, m, 'male')
        t_f_d, t_f_z = get_dist(t, name_index, c, m, 'female')
        if t_m_d is not None and t_f_d is not None:
            d = hellinger(t_m_d, t_f_d)
        else:
            d = 0
        
        log.debug('Window {}\td {:.3f}'.format(t, d))
        ds.setdefault(t, {})[m] = d
data = []
index = []
for y, d in sorted(ds.iteritems()):
    d['year'] = y
    data.append(d)
    index.append(y)
#diffs = pd.rolling_mean(pd.DataFrame(data, index=index, columns=['TV', 'FILM']), 5)
diffs = pd.DataFrame(data, index=index, columns=['TV', 'FILM'])

#tv_corr = pd.rolling_corr(counts['TV count'], diffs['TV'], window=5) + 1
#film_corr = pd.rolling_corr(counts['FILM count'], diffs['FILM'], window=5) + 1

# Plotting
STYLES = {
    'TV': ('g', '-'),
    'TV count': ('g', '--'),
    'TV Count Correlation': ('g', '--'),
    'FILM': ('r', ':'),
    'FILM count': ('r', '-.'),
    'FILM Count Correlation': ('r', '-.'),
}

#sns.set_style('white', {'xtick.major.size': 0})
fig, ax1 = plt.subplots()

lines, labels = [], []

for df, a in zip((diffs,), (ax1,)):
    for c in df.columns:
        color, style = STYLES[c]
        lines.append(a.plot(df.index, getattr(df, c), color=color, ls=style)[0])
        labels.append(c)

ax1.legend(lines, labels, loc=2)
ax1.set_ylabel('Inter-gender Hellinger delta', rotation=90)
ax1.set_xlabel('Year')
ax1.set_ylim(0, 1)
ax1.set_xlim(left=EARLIEST_YEAR, right=LATEST_YEAR-1)
plt.savefig('inter-gender-rolling-hellinger.pdf')
#plt.show()
