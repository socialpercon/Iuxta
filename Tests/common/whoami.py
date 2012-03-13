#!/usr/bin/env python
def whoami():
    import sys
    return sys._getframe(1).f_code.co_name
    
def blah(): pass