#!/usr/bin/env python
import csv
import sys

w = csv.writer(sys.stdout, delimiter=',')
for row in sys.stdin:
    row = row.rstrip().split('\t')
    w.writerow(row)
