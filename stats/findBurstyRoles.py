# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 17:19:28 2015

@author: mgalle
@pickle: finds bursty periods in movie database
"""

from utils import argparser_factory, pd, np, properNames
from collections import defaultdict
import cPickle as pkl
import pybursts
import kleinberg

# FIXME Needs to filter by medium.
""" path contains the DataFrame obtained through the following
c.execute('''
SELECT name, year, SUM(count) AS total, SUM(count*female) AS ftotal, SUM(count*female) / SUM(count) AS pf
FROM parts
GROUP BY name, year
ORDER BY pf DESC''')


df = pd.DataFrame(c.fetchall(), columns=['name', 'year', 'total', 'ftotal', 'pf'])



"""

def load(path):
    with open(path) as f:
        return pkl.load(f)



"""
    returns total sum of occurrences over @param keyw
"""
def getSum(df,keyw):
    counter=defaultdict(int)
    for i,row in df.iterrows(): 
        counter[row[keyw]] +=  row['total']
    return counter

"""
    return array with total roles in the window [start,end]
"""
def getTotals(df,start=1950,end=2014):
    yearc=getSum(df,'year')
    return np.array([yearc[x] for x in xrange(start,end+1)], dtype=np.float64)


"""
    returns (frequency,role) such that frequency >= threshold
"""
def frequentRoles(df,threshold):
    roleCounter = getSum(df,'name')
    
    return filter(lambda x : x[0] >= threshold, zip(roleCounter.values(), roleCounter.keys()))


"""
    run like
    $> findBurstyPeriods( df[df['name']==rolename], getTotals(df) )
"""
def findBurstyPeriods(role,totals,start=1950,end=2014):
    freq=defaultdict(int, dict( [ (row['year'],row['total']) for i,row in role.iterrows() ] ))
    f=np.array([freq[x] for x in xrange(start,end+1)])
    k=kleinberg.kleinberg(f+np.spacing(1),totals,.1,2,names=range(start,end+1))
    bursts,score = k.burstyFeatures()

    for score,period,kind in k.translate(bursts):
        yield score,period,kind,role.iloc[0]['name']



def burstyRoles(df):
    df=df[df['year'].isin(range(1950,2015))]

    roless = set([x[1] for x in frequentRoles(df,200)])
    roless = roless.difference(properNames())
    
    totals = getTotals(df)
    bursts = []
    for rolename in roless:
        print rolename
        for burst in findBurstyPeriods(df[df['name']==rolename],totals):
            bursts.append (burst)
    
    B = [(score,y[0],y[-1],t,n) for (score,y,t,n) in sorted(bursts,reverse=True)]
    
    print "OVER-REPRESENTED"
    for score,startyear,endyear,_,role in filter(lambda x : x[3]==2, B)[:50]:
        print '{} -- {}\t{}\t({:.2f})'.format(startyear,endyear,role,score)


    print "UNDER-REPRESENTED"
    for score,startyear,endyear,_,role in filter(lambda x : x[3]==0, B)[:50]:
        print '{} -- {}\t{}\t({:.2f})'.format(startyear,endyear,role,score)


"""
    maps into exponential distribution
    problem:
        no normalization by total numbers!
"""
def findBurstyPeriodsOld(role,totals):

    maxR = max(role['total'])    
    freqs = []
    for i, row in role.iterrows():
        year = row['year']
        if year > 2014: continue
        freq = row['total']
        freqs.append( (year,freq))
    
    freqs = sorted(freqs)
    gaps = []
    for (year,freq) in freqs:
        gaps.extend([ (year, maxR/freq) ] * freq )
        
    
    
    bursts = pybursts.kleinberg([x[1] for x in gaps], s=2, gamma=0.1)
    for burst in bursts[1:]:
        print burst[0],gaps[burst[1]][0], gaps[burst[2]-1][0]
        
        
if __name__ == '__main__':
    p = argparser_factory()
    args = p.parse_args()
    df = load(args.db)
