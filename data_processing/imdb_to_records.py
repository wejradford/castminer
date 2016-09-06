#!/usr/bin/env python
"""

Abbott, Paul (III)  Built for Speed (2006) (TV) {{SUSPENDED}}  [Himself]
            "2000 American League Championship Series" (2000) {Game 4}  [Himself - Seattle Mariners Pitcher]
            "2001 American League Championship Series" (2001) {Game 4}  [Himself - Seattle Mariners Pitcher]

Abbott, Paul (V)    8 Dates with Paul (2010)  [Paul Senior]  <3>
"""
import argparse
import re
import sys

BRACKETS = re.compile(r'\[([^\]]+)\]')
AS_PARENS = re.compile(r'\(as ([^)]+)\)', re.IGNORECASE)
YEAR = re.compile('\(([0-9]{4})\)')
TITLE = re.compile('^([^(]+) ')
RANK = re.compile('<([0-9]+)>')

EPISODE = re.compile('{(([^(}]+) ?)?(\(([^}]*)\))?}')
SPACES = re.compile(' +')

SELVES = set('''
himself
herself
theirselves
'''.strip().split('\n'))

a = argparse.ArgumentParser()
a.add_argument('gender')
a.add_argument('--companies')
args = a.parse_args()

looking = False
gender = args.gender
companies = {}
if args.companies:
    with open(args.companies) as f:
        for line in f:
            name, country = line.decode('utf8').rstrip().split('\t')
            companies[name] = country

for line in sys.stdin:
    line = line.rstrip().decode('iso_8859-1')
    if looking:
        if line.startswith('----'):
            continue
        if not line.strip():
            # Flush
            pass
        else:
            parts = [i for i in line.split('\t') if i]
            if len(parts) == 2:
                name, role = parts
            elif len(parts) == 1:
                role = parts[0]
            else:
                print >> sys.stderr, '#split', parts
                continue

            # Check for (credit_only) or {{SUSPENDED}} or themselves
            if '(credit_only)' in role or '{{SUSPENDED}}' in role or 'themselves' in role.lower():
                continue

            # Try to find a year.
            try:
                year = YEAR.findall(role)[0]
            except IndexError:
                continue

            # Try to find a role in square brackets.
            try:
                as_role_name = AS_PARENS.findall(role)[0]
            except IndexError:
                as_role_name = None
                
            try:
                role_name = BRACKETS.findall(role)[0]
            except IndexError:
                if as_role_name is not None:
                    role_name = as_role_name
                else:
                    #print >> sys.stderr, '#missing_brackets', line.encode('utf8')
                    continue

            # Repair "Herself" if we have an "(as ROLE)" supplied.
            if role_name.lower() in SELVES and as_role_name is not None:
                role_name = as_role_name
            role_name = role_name.strip()
            if not role_name:
                continue

            # Try to find a cast list rank in angle brackets.
            try:
                rank = int(RANK.findall(role)[0])
            except IndexError:
                rank = 0 # Ranks are 1-indexed.

            # Check remainder.
            remainder = EPISODE.sub('(EPISODE)', TITLE.sub('', role))
            remainder = remainder.replace(u'({})'.format(year), '').replace(u'[{}]'.format(role_name), '').replace(u'(as {})'.format(role_name), '').replace('<{}>'.format(rank), '').strip()
            remainder = remainder.replace('[', '(').replace(']', ')')
            remainder = SPACES.sub('_', remainder).replace(')_(', ') (').split()
            
            voice = False
            genres = set()
            remaining_tags = []
            for tag in remainder:
                handled = False
                if tag == '(TV)' or 'episode' in tag.lower():
                    genres.add('TV')
                    handled = True
                # Straight to video could have been at a cinema.
                elif tag == '(V)':
                    genres.add('FILM')
                    handled = True
                elif tag == '(VG)':
                    genres.add('GAME')
                    handled = True
                if 'voice' in tag:
                    voice = True
                    handled = True
                if not handled:
                    remaining_tags.append(tag)
            if len(genres) > 1:
                print >> sys.stderr, '#genres {}'.format(genres), line.encode('utf8')
                continue
            elif not genres:
                genre = 'FILM'
            else:
                genre = list(genres)[0]
            remainder = ' '.join(remaining_tags)

            # Check for production country code.
            if '}' in role:
                title = role.split('}')[0] + '}'
            else:
                title = role.split(')')[0] + ')'
            country = companies.get(title, None)

            #print '*' + role.encode('utf8')

            print u'{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(name, role_name, year, gender, rank, genre, int(voice), country, remainder).encode('utf8')
    elif line.startswith('Name') and line.endswith('Titles'):
        looking = True
