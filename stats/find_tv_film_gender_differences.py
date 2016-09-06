#!/usr/bin/env python

from __future__ import print_function
from utils import argparser_factory, db_factory, pd, np, DEFAULT_MEDIUM, MEDIA

def video_to_film(i):
    if i[1] == 'VIDEO':
        i[1] = 'FILM'
    return i

p = argparser_factory()
p.add_argument('-w', '--window', default=5, type=int)
args = p.parse_args()

db = db_factory(args.db)
c = db.cursor()
c.execute('''
SELECT year, medium, name, count, female, male
FROM parts 
WHERE count > 20 
AND {}
ORDER BY year, name, medium'''.format(MEDIA[DEFAULT_MEDIUM]))

data = [video_to_film(i) for i in c.fetchall()]

df = pd.DataFrame(data, columns=['year', 'medium', 'name', 'count', 'pf', 'pm'])
media_deltas = []
for name, group in df.groupby(['name']):
    for year, year_group in group.groupby('year'):
        if len(year_group) != 2:
            continue
        pfs = {r.medium: r.pf for m, r in sorted(year_group.iterrows())}
        if not 'FILM' in pfs or not 'TV' in pfs:
            continue
        media_deltas.append({'name': name, 'year': year, 'FILM': pfs['FILM'], 'TV': pfs['TV'], 'd': pfs['TV'] - pfs['FILM']})

df = pd.DataFrame(media_deltas)
grouped = df.groupby('name')
rows = []
for name, group in sorted(grouped):
    count = len(group)
    mean_film = np.mean(group['FILM'])
    mean_tv = np.mean(group['TV'])
    mean_d = np.mean(group['d'])
    std_d = np.std(group['d'])
    rows.append((name, count, mean_film, mean_tv, mean_d, std_d))
rows.sort(key=lambda i: i[4])
print('Role\tn_years\tmean(p(f|FILM))\tmean(p(f|TV))\tmean(delta)\tstd(delta)')
for name, count, mean_film, mean_tv, mean_d, std_d in rows:
    print(u'{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}'.format(name, count, mean_film, mean_tv, mean_d, std_d).encode('utf8'))
