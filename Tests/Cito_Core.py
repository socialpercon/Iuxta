#!/usr/bin/env python
from Queue import Queue
from string import letters
from common import urls, users, mechBrowser, conversions, timed
from common.whoami import whoami as wai
from common.smartmath import smin, smax, savg

from matplotlib.pyplot import *
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

import mechanize, cookielib, urlparse
import threading, time, random
import glob, os, csv
#-------------------------------------

colors = {
    'gMax':['k:','black'],
    'gAvg':['y-','yellow'],
    'cMin':['go','green'],
    'cMax':['ro','red']
}

ACTIVEUSERS = 0

cycleDict = {}
pDict = {}
trafficDict = {}
errorDict = {}
serverDict = {}

#Records the current server
def recServ(pkey):
    x = serverDict.setdefault(pkey, 0)
    serverDict[pkey] = x + 1

#Records encountered errors in the thread RUN
def errorRec(pkey):
    errorDict.setdefault(pkey, 0)
    errorDict[pkey] = errorDict[pkey] + 1

#Records the ingoing/outgoing traffic
def traffRec(pkey, bytes, download=True):
    trafficDict.setdefault(pkey, {'download':0,'upload':0})
    if download: trafficDict[pkey]['download'] = trafficDict[pkey]['download'] + bytes
    else: trafficDict[pkey]['upload'] = trafficDict[pkey]['upload'] + bytes

#Records time to function call in performance dictionary
def rec(pkey, t):
    x = cycleDict.setdefault(pkey, [])
    x.append(time.time() - t)

#-------------------------------------
def callTest(pTest,                             #Test module to run
             usrStart = 0,                      #Drone starting ID number
             usrEnd = 100,                      #Drone ending ID number
             usrChunk = 5,                      #X amount of Drones per Cycle
             usrCycle = 20,                     #X seconds sperating saturation cycles
             totalFiles = [],                   #Queued activities
             userObject = users.ducotDrones,    #Drones to use for testing
             urlPack = urls.ducotURLpack,       #URLS to use for testing
             spreadsheet = r''):                #Spreadsheet to read values from.
    
    for step in filter(lambda x: x.split("_")[0] == "step", dir(pTest)):
        pDict[step], cycleDict[step] = [], []

    def statit():
        print "~%d / %d"%(queue.qsize(), len(totalFiles))
        if running: threading.Timer(poll, statit).start()
        for k in pDict.keys():
            c = graphData.setdefault(k, {
                    'gMax':[], 'gAvg':[], 'cMin':[], 'cMax':[]
            })

            c['gMax'].append(smax(pDict[k])) #graph max
            c['gAvg'].append(savg(pDict[k])) #graph average
            c['cMin'].append(smin(cycleDict[k])) #cycle minimum
            c['cMax'].append(smax(cycleDict[k])) #cycle max
            
        #clear cycle statistics
        for k in cycleDict.keys():
            pDict[k] = pDict[k]+cycleDict[k]
            cycleDict[k] = []
    
    def spawnUsers():
        global ACTIVEUSERS
        
        if not queue.empty() and ACTIVEUSERS + chunk <= userCount:            
            if running: threading.Timer(cycle, spawnUsers).start()
            for i in xrange(0, chunk):
                uname = userObject["user"] + str(usrStart+ACTIVEUSERS+i)
                t = pTest(mechBrowser.BrowserInstance(),
                          uname,
                          users.password,
                          random.choice(userObject["cabinets"]),
                          queue,
                          urlPack,
                          ssDict.get(uname, {}))
                t.setDaemon(True)
                t.start()
            
            ACTIVEUSERS += chunk  
            graphUsers.append((ACTIVEUSERS, int(time.time() - start)))
            print "%d running in the pool for %ds"%(ACTIVEUSERS, time.time() - start)

    queue = Queue()
    start = time.time()
    running = True

    graphData = {}
    graphUsers = []
    
    userCount = usrEnd - usrStart #max users per instance
    chunk = usrChunk #users to add every cycle
    cycle = usrCycle #seconds
    poll = 1 #seconds

    #read CSV file
    ssDict = {}
    if spreadsheet != '':
        import re
        reader = csv.reader(open(spreadsheet, 'rb'), delimiter=',')
        header = reader.next()
        accessIndex = header.index('ACCESS')
        ssDict['header'] = header

        for row in reader:
            usr = re.search(r'nd.automated-drone_\d+', row[accessIndex]).group(0) 
            cur = ssDict.setdefault(usr, [])
            cur.append(row)

        for row in ssDict.keys():
            ssDict[row].append(header)
        
    for f in totalFiles:
        queue.put(f)
    
    spawnUsers()
    statit()
    
    #block here until all jobs in queue are complete
    queue.join()
    
    results = {
        'TNAME': pTest.__name__, #string
        'USERS': ACTIVEUSERS, #int
        'ITEMS': totalFiles, #list
        'TIME':  time.time() - start, #int
        'GDATA': (graphData, graphUsers) #(dict, list)
    }

    running = False
    return results

#prints the statistics graph
def printStats(tresults):
    #text portion of the generated PDF file
    def getTextReport(tresults):
        rtn = ""
        rtn += "%s, FINISHED with %s users on %s items in %0.2fs\nFinished @ %s\n"%(
            tresults['TNAME'], tresults['USERS'], len(tresults['ITEMS']), tresults['TIME'], time.asctime())
        for step in serverDict.keys():
            rtn += "\n%s used %d times.\n"%(step, serverDict[step])
        rtn += "-"*70
        
        averages = {
            'min':0, 'max':0, 'avg':0
        }
        
        for step in sorted(pDict.keys()):
            c = pDict[step]
            rtn += "\n%s \n\tmin:%0.3fs \tavg:%0.3fs \tmax:%0.3fs"%(step, smin(c), savg(c), smax(c))
            averages['min'] += smin(c)
            averages['avg'] += savg(c)
            averages['max'] += smax(c)
            
        a = len(pDict.keys())
            
        rtn += "\n\n\n\tmin:%0.3fs \tavg:%0.3fs \tmax:%0.3fs\n"%(averages['min']/a, averages['avg']/a, averages['max']/a)
       
        rtn += "\n\nBandwidth accumulated\n"
        rtn += "-"*70
        
        averages = {
            'up':0, 'down':0
        }
        
        for step in sorted(trafficDict.keys()):
            rtn += "\n%s \n\tdownload:%9s \tupload:%9s"%(step, conversions.convert_bytes(trafficDict[step]['download']), conversions.convert_bytes(trafficDict[step]['upload']))
            averages['up'] += trafficDict[step]['upload']
            averages['down'] += trafficDict[step]['download']
        
        rtn += '\n\n\n\tdownload:%9s \tupload:%9s\n'%(conversions.convert_bytes(averages['down']), conversions.convert_bytes(averages['up']))
        
        rtn += "\n\nKnown errors\n"
        rtn += "-"*70
        total = 0
        for step in sorted(errorDict.keys()):
            rtn += "\n%25s count: %d"%(step, errorDict[step])
            total += errorDict[step]
            
        rtn += "\nTotal:%d"%(total)
        
        rtn += "\n\nItems used: \n"
        rtn += "-"*70
        for step in tresults['ITEMS']:
            rtn += "\n" + str(step)

        return rtn

    def writeLog(tresults, tstamp):
        filename = tstamp + ".log"
        f = open("logs/" + filename, "w")
        f.write(getTextReport(tresults))
        f.close()

    #Prepare for printing graphs and PDF
    
    stamp = str(int(time.time())) + "_" + tresults['TNAME']
    
    rDict = tresults['GDATA'][0] # test data
    uData = tresults['GDATA'][1] # user saturation data
    
    fname = stamp + ".pdf"
    
    pp = PdfPages("logs/" + fname)
    
    for k in rDict.keys():
        plt.figure(k, dpi=300)
        plt.grid(True, linestyle="--", alpha=".3", color="black")
        plt.xlabel('Elapsed Time (s)')
        plt.ylabel('Execution Time (s)')
        plt.suptitle('%s: %s'%(tresults['TNAME'], k), fontsize=15, fontweight='bold')
        
        stepResults = rDict[k] #dictionary
        
        for i, g in enumerate(stepResults.keys()):
            X = range(0, len(stepResults[g]))
            Y = stepResults[g]
            
            if g == 'gAvg': plt.fill_between(X, 0, Y, facecolor=colors[g][1], alpha=.2)           
            if g == 'cMin' or g == 'cMax':
                for e in zip(X, Y):
                    if e[1] > 0: plt.plot(e[0], e[1], colors[g][0], label=g, alpha=1.0)
            else: plt.plot(X, Y, colors[g][0], label=g, alpha=1.0)
            
        for user, xtime in uData:
            plt.plot(xtime, stepResults['gAvg'][xtime], 'k.', label='User Count')
            plt.text(xtime, stepResults['gAvg'][xtime]+.15, user, fontsize=7)

        plt.savefig(pp, format='pdf')        
    
    #stats = plt.figure()
    #stats.text(.1,.3, getTextReport(tresults), fontsize=10)
    #stats.savefig(pp, format='pdf')
    
    writeLog(tresults, stamp)
    pp.close()