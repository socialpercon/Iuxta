#!/usr/bin/env python
import os

if __name__ == "__main__":

    try:
        if not os.path.exists(r"C:\Temp\Cito"):
            os.makedirs(r"C:\Temp\Cito")
            print "Created Cito temp directory."
    except: print "Couldn't create Cito temp directory."
    
    try:
        import matplotlib
    except: print "Couldn't import matplot lib."
    
    try:
        import mechanize, cookielib, urlparse
    except: print "Couldn't import console browser Mecahnize."
    
    try:
        import threading, time, random, glob, os, uuid
    except: print "Couldn't import one or more threading libraries."
    
    try:
        import Cito_Core
    except: print "Couldn't import the Cito testing Core."

    try:
        from Queue import Queue
        from string import letters
        from common import urls, users, mechBrowser, conversions, timed
        from common.whoami import whoami as wai
        from common.smartmath import smin, smax, savg
    except: print "Couldn't import the bulk of Cito testing."

    print "Done."
    raw_input()    
