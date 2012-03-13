#!/usr/bin/env python

class get(object):
    def __init__(self):
        self.v = {}
        with open(r'common\private.config', 'r') as f:
            for x in f.readlines():
                if x[0] != "#":
                    a = x.split('=')
                    self.v[a[0].strip()] = a[1].strip()
    
    def __getitem__(self, key):
        return self.v.get(key, '')
