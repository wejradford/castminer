# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 10:37:04 2015

@author: mgalle
@brief: implements a modified version of Kleinberg's bursty feature detector [1].
        uses three states: under, normal, over (bursty)

[1] Kleinberg, Jon. "Bursty and hierarchical structure in streams." Data Mining and Knowledge Discovery 7.4 (2003): 373-397.
"""
import numpy as np
import sys

"""
    modified Kleinberg's bursty feature detector
    have three states: under-represented, normal, over-represented

"""

infty = sys.float_info.max
class kleinberg:
    def __init__(self,freq,totalfreq,gamma,s,names=None):
        
        if names is None:
            names = range(len(freq))
        assert len(freq) == len(names)
        assert len(freq) == len(totalfreq)
        
        self.freq = freq
        self.n = len(self.freq)
        self.totalfreq = totalfreq
        self.names = names
        
        self.p = sum(freq)/float(sum(totalfreq))
        self.gamma = gamma
        self.s = s

        # convention: 0 -> under, 1-> normal, 2->over
        # cost of going back to 1 is 0.
        # cost of going from 1 to [0|2] is cost and you can't go directly 0 <-> 2
        cost = gamma * np.log2(self.n)
        #self.transition = np.vstack([ [0.,0.,2*cost], [cost,0.,cost], [2*cost,0,0] ])
        #self.transition = np.vstack([ [0.,cost,2*cost], [0,0.,cost], [0,0,0] ])
        self.transition = np.vstack([ [0.,0.,infty], [cost,0.,cost], [infty,0,0] ])
    
    
    def emissioncost(self,i,state):
        if state == 1:
            p = self.p
        elif state == 0:
            p = self.p / self.s
        else:
            assert state == 2
            p = self.s * self.p
        assert p<1
#        p = self.p * (state+1)
        d,r  = self.totalfreq[i], self.freq[i]
        ln = np.log2
        # using Stirling approximation (first term only)
        coef = d * ln(d) - (d-r) * ln(d-r) - r * ln (r)
        return - (coef + r * ln(p) + (d-r) * ln(1 - p))
    
    
    """
        runs bursty feature detection
    """
    def burstyFeatures(self):
        best = [0] * 3
        icamefrom = -1 * np.ones((self.n,3))
        
        for i in xrange(self.n):
            newbest = [infty] * 3
            for state in xrange(3):
                for laststate in xrange(3):
                    contender = best[laststate] + self.transition[laststate][state] + self.emissioncost(i,state)
                    if contender < newbest[state]:
                        newbest[state] = contender
                        icamefrom[i][state] = laststate
            best = newbest
    
        #print icamefrom,best
        
        
        # translate by backtracking
        state = np.argmin(best)
        score = best[state]

        paths = [state]        
        for i in range(self.n-1,-1,-1):
            state = icamefrom[i][state]
            paths.append(int(state))
        
        paths.reverse()
        return np.array(paths[1:]), score
    
    
    """
        takes an array of bursts (as returned by burstyFeatures) and translates it into tuples of
            score, window (using self.names), ID (0->under, 2->over)
    """
    def translate(self,bursts):
        old = -1
        score = 0
        window = []
        for i in xrange(len(bursts)):
            if bursts[i] == old:
                window.append(self.names[i])
                score += self.emissioncost(i,1) - self.emissioncost(i,old)
            else:
                if old != 1 and window != []:
                    yield score,window,old
                window = [self.names[i]]
                score = self.emissioncost(i,1) - self.emissioncost(i,bursts[i])
            old = bursts[i]
    
    
    
    
    
    
    
    