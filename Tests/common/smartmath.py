#!/usr/bin/env python

def smin(lst):
    if lst: return min(lst)
    else: return 0
    
def smax(lst):
    if lst: return max(lst)
    else: return 0

def savg(lst):
    if lst: return sum(lst)/len(lst)
    else: return 0