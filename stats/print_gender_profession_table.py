#!/usr/bin/env python

from __future__ import print_function
from utils import argparser_factory, db_factory

p = argparser_factory()
args = p.parse_args()

OR = ' OR '
SEARCH = 'name LIKE "%{}%"'
PREFIX = 'name LIKE "{}%"'
MATCH = 'name = "{}"'

TERMS = {
    'IT': {'search': ('software', 'computer', 'hacker')},
    'Medical': {'search': ('medical', 'dr', 'doctor', 'surgeon', 'psychiatrist')},
    'Corporate': {'search': ('corporate', 'ceo', 'coo')},
    'Law': {'search': ('prosecutor', 'lawyer')},
    'Politics': {
        'search': ('minister', 'dictator', 'parliament', 'senator'),
        'match': ('president',),
    },
    'Science': {'search': ('science', 'professor')},
    'Religion': {
        'search': ('priest', 'priestess', 'reverend', 'pastor', 'prior', 'allamah', 'imam', 'rabbi', 'guru', 'lama', 'ayatollah', 'swami'),
        'prefix': ('bishop',),
    },
    'Engineering': {'search': ('engineer',)},
}

db = db_factory(args.db)
c = db.cursor()
header = []
columns = []
for profession, terms in TERMS.iteritems():
    clauses = []
    clauses.extend([SEARCH.format(t) for t in terms.get('search', [])])
    clauses.extend([PREFIX.format(t) for t in terms.get('prefix', [])])
    clauses.extend([MATCH.format(t) for t in terms.get('match', [])])
    # FIXME Exclude media....
    q = '''
    SELECT SUM(female * count) / SUM(count)
    FROM parts
    WHERE {}'''.format(OR.join(clauses))
    c.execute(q)
    (p,) = c.fetchone()
    print('{}\t{:.2f}\t{}'.format(profession, p, terms))
