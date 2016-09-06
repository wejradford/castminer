import argparse
from collections import Counter
import csv
import logging
import os
import math
import sqlite3

log = logging.getLogger()

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
np.random.seed(sum(map(ord, "aesthetics")))
import seaborn as sns

FONT_SIZE = 18

def set_sns_style(font_size=FONT_SIZE):
    settings = {
        'legend.frameon': True, 
        'grid.color': '0.95',
        'xtick.labelsize': font_size,
        'ytick.labelsize': font_size,
        'legend.fontsize': font_size,
        'font.family': 'serif',
        'xtick.major.size': 0,
    }
    sns.set_style("white", settings)

EARLIEST_YEAR = 1900
LATEST_YEAR = 2014
HEIGHT = 5
WIDTH = 10
LINE_WIDTH = 3.5

FIGS = os.path.join(os.path.dirname(__file__), 'figs')
assert os.path.isdir(FIGS)

DECADES = [
    (1900, 1920),
    (1920, 1940),
    (1940, 1960),
    (1960, 1980),
    (1980, 2000),
    (2000, 2020),
]

def argparser_factory():
    p = argparse.ArgumentParser()
    p.add_argument('--db')
    p.add_argument('--width', type=int, default=WIDTH)
    p.add_argument('--height', type=int, default=HEIGHT)
    p.add_argument('--font-size', type=float, default=FONT_SIZE)
    logging.basicConfig(level=logging.INFO)
    return p

def db_factory(db_filename):
    return sqlite3.connect(db_filename)

def z_proportion(n1, n2, x1, x2, lower_x=5):
    assert x1 <= n1, 'Count 1 must be lower than total 1\t{}\t{}'.format(x1, n1)
    assert x2 <= n2, 'Count 2 must be lower than total 2\t{}\t{}'.format(x2, n2)
    inv_x1 = n1 - x1
    inv_x2 = n2 - x2
    if any(i < lower_x for i in (x1, x2, inv_x1, inv_x2)):
        logging.warning('Invalid z proportion test\tx1/inv\t{}/{}\tx2/inv\t{}/{}'.format(x1, inv_x1, x2, inv_x2))
        return None
    p1 = x1 / float(n1)
    p2 = x2 / float(n2)
    p = (x1 + x2) / float(n1 + n2)
    return (p1 - p2) / math.sqrt((p * (1-p)) * (1/float(n1) + 1/float(n2)))

def set_axis_font_size(a, size=FONT_SIZE):
    for item in ([a.title, a.xaxis.label, a.yaxis.label] +
                 a.get_xticklabels() + a.get_yticklabels()):
        item.set_fontsize(size)

def plot_role_counts(counts, label, fname, window=5, 
                     width=WIDTH, height=HEIGHT, font_size=FONT_SIZE):
    df = pd.DataFrame(counts)
    rm = pd.rolling_mean(df, window)
    
    set_sns_style(font_size)
    fig, ax1 = plt.subplots(figsize=(width, height))
    ax1.plot(rm.index, rm['Count'], lw=LINE_WIDTH)
    set_axis_font_size(ax1, font_size)
    
    # Ducks.
    ax1.set_ylabel('Count', rotation=90)
    ax1.set_xlabel('Year')
    ax1.set_ylim(0)
    ax1.set_xlim(left=EARLIEST_YEAR, right=LATEST_YEAR)
    plt.savefig(fname)

STYLES = {
    'M': ('g', '-', None),
    'F': ('b', '--', None),
    'p(F)': ('r', ':', None),
    'TV': ('g', '-', '--'),
    'FILM': ('r', ':', '-.'),
}
def plot_gender_counts_pf(counts, label, window=5, 
                          earliest_year=EARLIEST_YEAR,
                          width=WIDTH, height=HEIGHT, 
                          font_size=FONT_SIZE):
    set_sns_style(font_size) 
    df = pd.DataFrame(counts)
    rm = pd.rolling_mean(df, window)
    lines = []
    labels = []
    fig, ax1 = plt.subplots(figsize=(width, height))
    for c in ['F', 'M']:
        color, style, _ = STYLES[c]
        lines.append(ax1.plot(rm.index, getattr(rm, c), color=color, 
                              ls=style, lw=LINE_WIDTH)[0])
        labels.append(c)

    # Plot gender series.
    ax2 = ax1.twinx()
    c = 'p(F)'
    color, style, _ = STYLES[c]
    lines.append(ax2.plot(rm.index, rm[c], color=color,
                          ls=style, lw=LINE_WIDTH)[0])
    labels.append(c)

    # Ducks.
    ax1.legend(lines, labels, loc=2, fontsize=font_size)
    ax1.set_ylabel('Count', rotation=90)
    ax1.set_xlabel('Year')
    ax1.set_ylim(0)
    ax1.set_xlim(left=earliest_year, right=LATEST_YEAR)
    ax2.set_ylim(0, 1)
    ax2.set_ylabel('p(F)', rotation=90)
    ax2.set_xlim(left=earliest_year, right=LATEST_YEAR)
    set_axis_font_size(ax1, font_size)
    set_axis_font_size(ax2, font_size)

    plt.savefig(os.path.join(FIGS, '{}.rm-{}.pdf'.format(label.replace(' ', '_'), window)))

def plot_gender_counts_pf_by_medium(counts, p_females, label, width=WIDTH, 
                                    height=HEIGHT, window=5, font_size=FONT_SIZE,
                                    earliest_year=EARLIEST_YEAR):
    set_sns_style(font_size) 
    df = pd.DataFrame(counts)
    rm = pd.rolling_mean(df, window)

    # Plot medium series.
    lines = []
    labels = []
    fig, ax1 = plt.subplots(figsize=(width, height))
    for c in rm.columns:
        color, style1, style2 = STYLES[c]
        lines.append(ax1.plot(rm.index, getattr(rm, c), color=color, 
                              ls=style1, lw=LINE_WIDTH)[0])
        labels.append(c)
    set_axis_font_size(ax1, font_size)

    # Plot gender series.
    ax2 = ax1.twinx()
    df = pd.DataFrame(p_females)
    rm = pd.rolling_mean(df, window)
    for c in rm.columns:
        color, style1, style2 = STYLES[c]
        lines.append(ax2.plot(rm.index, getattr(rm, c), color=color, 
                              ls=style2, lw=LINE_WIDTH)[0])
        labels.append('p(f|{})'.format(c))
    set_axis_font_size(ax2, font_size)

    # Ducks.
    ax1.legend(lines, labels, loc=2, fontsize=font_size)
    ax1.set_ylabel('Count', rotation=90)
    ax1.set_xlabel('Year')
    ax1.set_ylim(0)
    ax1.set_xlim(left=earliest_year, right=LATEST_YEAR)
    ax2.set_ylim(0, 1)
    ax2.set_ylabel('p(F)', rotation=90)
    ax2.set_xlim(left=earliest_year, right=LATEST_YEAR)

    plt.savefig(os.path.join(FIGS, '{}.rm-{}.pdf'.format(label.replace(' ', '_'), window)))

def read_imdb_census_mapping(f):
    labels = set()
    label_to_imdb = {}
    label_to_census = {}
    for label, imdb_role, census_label in csv.reader(f, delimiter='\t'):
        if label.startswith('#'):
            continue
        labels.add(label)
        label_to_imdb.setdefault(label, set()).add(imdb_role)
        label_to_census.setdefault(label, set()).add(census_label)
    return labels, label_to_imdb, label_to_census

def read_census_data(f):
    counts = {}
    p_fs = {}
    for row in csv.DictReader(f, delimiter='\t'):
        # Remove blanks.
        row = {k: v for k, v in row.iteritems() if v}
        role = row.pop('Role')
        for year, raw in row.iteritems():
            year = int(year)
            count, percent_f = raw.lstrip('(').rstrip(')').split()
            count = float(count.rstrip(',')) * 1000
            p_f = float(percent_f) / 100.0 if percent_f != -1 else 0
            counts.setdefault(year, {})[role] = count
            p_fs.setdefault(year, {})[role] = p_f

    return pd.DataFrame(counts), pd.DataFrame(p_fs)


# Media.
MEDIA = {
    None: '',
    'TV': "medium = 'TV'",
    'FILM': "(medium = 'FILM' OR medium = 'VIDEO')",
    'FILM+TV': "(medium = 'FILM' OR medium = 'VIDEO' OR medium = 'TV')",
}
DEFAULT_MEDIUM = 'FILM+TV'


def get_all_role_counts(cursor, medium=DEFAULT_MEDIUM):
    cursor.execute('''
    SELECT year, SUM(count), SUM(count * female) / SUM(count)
    FROM parts
    WHERE {}
    GROUP BY year;'''.format(MEDIA[medium]))
    counts = {}
    total = 0
    for year, count, p_female in cursor.fetchall():
        counts.setdefault('Count', {})[year] = count
        total += count
    return counts, total
    

def get_gender_roles_for_year(cursor, year, medium=DEFAULT_MEDIUM, country=None):
    if country is None:
        country_q = ''
        bindings = (year,)
    else:
        country_q = ' AND country = ?'
        bindings = (year, country)
    q = '''
    SELECT name, SUM(count), SUM(CAST(count*female AS INT))
    FROM parts
    WHERE year = ? 
    AND {} 
    {}
    GROUP BY name'''.format(MEDIA[medium], country_q)
    cursor.execute(q, bindings)
    return {i[0]: (i[1], i[2]) for i in cursor.fetchall()}


def get_gender_counts_for_year(cursor, role=None, medium=DEFAULT_MEDIUM):
    q = '''
    SELECT year, SUM(count * female), SUM(count * (1-female)), SUM(count * female) / SUM(count) 
    FROM parts
    WHERE {}'''.format(MEDIA[medium])
    binding = tuple()
    if role is not None:
        q += ' AND name LIKE ?'
        binding = ('%{}%'.format(role),)
    q += ' GROUP BY year'
    cursor.execute(q, binding)
    counts = {}
    for year, f_count, m_count, p_female in cursor.fetchall():
        counts.setdefault('M', {})[year] = m_count
        counts.setdefault('F', {})[year] = f_count
        counts.setdefault('p(F)', {})[year] = p_female
    return counts

def plot_census_comparison(data, year, medium, font_size=FONT_SIZE):
    set_sns_style(font_size) 
    labels_z = {i['role']: i['z'] for i in data}
    labels = [i['role'] for i in data]
    imdb = [i['IMDb'] for i in data]
    census = [i['Census'] for i in data]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_xlabel('p(F|OES @ {})'.format(year))
    if medium:
        ax.set_ylabel('p(F|IMDb {} @ {})'.format(medium, year))
    else:
        ax.set_ylabel('p(F|IMDb @ {})'.format(year))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.scatter(census, imdb)
    ax.plot([0, 1], [0, 1], ls='--', color='gray', alpha=0.6)
    set_axis_font_size(ax, font_size)
    for l, x, y in zip(labels, census, imdb):
        z = labels_z.get(l)
        if z is not None and abs(z) > 1.96:
            l += '+'
        
        xytext = (-1, 1)
        va = 'bottom'
        ha = 'right'
        '''
        if l.startswith('nurse'):
            va = 'top'
        if l.startswith('pilot'):
            ha = 'left'
        '''
        ax.annotate(l, xy=(x, y), xytext=xytext,
                     textcoords='offset points', ha=ha, va=va,
                     fontsize=font_size,
        )
    plt.savefig(os.path.join(FIGS, 'IMDbVsCensus.{}.{}.pdf'.format(year, medium)))

def get_census_comparisons(mapping, census, cursor, focus_year=None, medium=DEFAULT_MEDIUM):
    # Read mappings.
    label, label_to_imdb, label_to_census = read_imdb_census_mapping(open(mapping))
    census_to_label = {}
    for label, c_labels in label_to_census.iteritems():
        for c_label in c_labels:
            if c_label in census_to_label:
                log.warning('Census label "{}" already mapped!'.format(c_label))
            else:
                census_to_label[c_label] = label

    # Read census data.
    counts, p_fs = read_census_data(open(census))

    unmapped_census, unmapped_census_years = Counter(), Counter()
    all_plot_data = {}
    # Scan each known year.
    for year, data in counts.iteritems():
        if focus_year and year != focus_year:
            continue
        log.info('Fetching roles for {}'.format(year))
        mapped = total = compared = 0
        plot_data = []
        imdb_roles = get_gender_roles_for_year(cursor, year, medium, country='us')

        # Cross-reference.
        mapped_counts, mapped_f_counts = Counter(), Counter()
        for census_role, census_count in data.iteritems():
            if np.isnan(census_count):
                continue

            # Try to match from census to label mapping.
            label = census_to_label.get(census_role)
            total += 1
            if label is None:
                unmapped_census[census_role] += census_count
                unmapped_census_years[census_role] += 1
                continue
            else:
                mapped += 1
                mapped_counts[label] += census_count
                mapped_f_counts[label] += p_fs[year][census_role] * census_count

        for label, total_census_count in sorted(mapped_counts.iteritems()):
            total_census_f_count = mapped_f_counts[label]

            # Try to map from label to IMDb.
            imdb_count = imdb_f_count = 0
            for imdb_role in label_to_imdb[label]:
                role_count, role_f_count = imdb_roles.get(imdb_role, (0, 0))
                log.info('Matched "{}" to "{}"\t{}\t{}'.format(label, imdb_role, role_count, role_f_count))
                imdb_count += role_count
                imdb_f_count += role_f_count

            z = z_proportion(imdb_count, total_census_count, imdb_f_count, total_census_f_count)
            if z is None:
                log.warning('Invalid z for "{}"\timdb {}\ttotal_census {}\tf_imdb {}\tf_census {}'.format(
                            label, imdb_count, total_census_count, imdb_f_count, total_census_f_count))
            if not imdb_count:
                continue
            compared += 1
            plot_data.append({'role': label, 'z': z, 'IMDb': imdb_f_count / float(imdb_count), 
                              'Census': total_census_f_count / float(total_census_count)})
        log.info('Mapped {} of {}\t{:.1f}%\tCompared {}'.format(mapped, total, 100*mapped/float(total), compared))
        if plot_data:
            all_plot_data[year] = plot_data
    return all_plot_data


def plot_census_comparison_line(df, annotations, fname, font_size=FONT_SIZE, width=WIDTH, height=HEIGHT):
    set_sns_style(font_size) 
    fig, ax1 = plt.subplots(figsize=(width, height))
    lines, labels = [], []
    for c, ls in zip(['Census', 'IMDb'], ['--', '-']):
        lines.append(ax1.plot(df.index, getattr(df, c), ls=ls, lw=5)[0])
        labels.append(c)
    for x, y in annotations:
        ax1.annotate('o', (x, y), fontsize=font_size, weight='bold')
    ax1.legend(lines, labels, fontsize=font_size)
    ax1.set_ylabel('p(F)', rotation=90)
    ax1.set_xlabel('Year')
    set_axis_font_size(ax1, font_size)
    plt.savefig(fname)


def plot_rolling_hellinger(df, fname, earliest_year, font_size=FONT_SIZE, 
                           width=WIDTH, height=HEIGHT):
    STYLES = {
        'TV': ('g', '-'),
        'TV count': ('g', '--'),
        'TV Count Correlation': ('g', '--'),
        'FILM': ('r', ':'),
        'FILM count': ('r', '-.'),
        'FILM Count Correlation': ('r', '-.'),
    }
    set_sns_style(font_size)
    fig, ax1 = plt.subplots(figsize=(width, height))

    lines, labels = [], []

    a = ax1
    set_axis_font_size(a, font_size)
    for c in df.columns:
        color, style = STYLES[c]
        lines.append(a.plot(df.index, getattr(df, c), color=color, 
                     ls=style, lw=LINE_WIDTH)[0])
        labels.append(c)
    ax1.legend(lines, labels, fontsize=font_size)
    ax1.set_ylabel('Inter-year distance', rotation=90)
    ax1.set_xlabel('Year')
    ax1.set_xlim(left=earliest_year, right=LATEST_YEAR-1)
    plt.savefig(fname)

"""
    load list of proper names
"""
def properNames(paths=['../data/malenames.txt','../data/femalenames.txt']):
    names = set()
    for path in paths:
        with open(path) as f:
            for l in f:
                names.add(l.strip().lower())
    return names
