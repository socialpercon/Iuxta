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
import glob, os
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

#-------------------------------------
def callTest(pTest, usrStart = 0, usrEnd = 100, usrChunk = 5, usrCycle = 20, totalFiles = [], userObject = users.ducotDrones, urlPack = urls.ducotURLpack):
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
                t = pTest(mechBrowser.BrowserInstance(), userObject["user"] + str(usrStart+ACTIVEUSERS+i), users.password, random.choice(userObject["cabinets"]), queue, urlPack)
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

    #totalFiles = xrange(0, 500)
    for f in totalFiles:
        queue.put(f)
    
    spawnUsers()
    statit()
    
    #block here until all jobs in queue are complete
    queue.join()
    
    results = {
        'TNAME':'Upload to Cabinet', #string
        'USERS': ACTIVEUSERS, #int
        'ITEMS': totalFiles, #list
        'TIME':  time.time() - start, #int
        'GDATA': (graphData, graphUsers) #(dict, list)
    }

    running = False
    return results

#-------------------------------------
class aaaTest(threading.Thread):
    def __init__(self, browserObject, username, password, cabinetID, queue, urlp):
        threading.Thread.__init__(self)
        
        self.up = urlp
        self.browser = browserObject.b
        self.username = username
        self.password = password
        self.cabID = cabinetID
        self.queue = queue
        
        self.timed = 0
        self.sizes = 0

#-------------------------------------
    def step_Login(self):
        def getServer(page):
            return filter(lambda x: "Patents" in x, page.split("</span>"))[0].split("(")[-1].strip(")")
        
        with timed.measure('%s, Logging in to netdocuments.'%(self.username)) as t:
            r = self.browser.open(self.up["URI_home"])
            s = r.read()
            traffRec(wai(), len(s))
            recServ(getServer(s))
            
            self.browser.select_form(name='loginform')
            self.browser['username'] = self.username
            self.browser['password'] = self.password
            r = self.browser.submit()
            
            traffRec(wai(), len(r.read()))
            rec(wai(), t)
    
    def step_Navigate(self, page, url):
        with timed.measure('%s, Navigating to %s.'%(self.username, page)) as t:
            try:
                r = self.browser.open(url)
                
                traffRec(wai(), len(r.read()))
            except: print "%s is moving on."
            rec(wai(), t)
    
    def step_UploadFile(self, uploadFile):
        filename = uploadFile.split("\\")[-1]
        fsize = int(os.path.getsize(uploadFile))
        with timed.measure('%s, Uploading file %s.'%(self.username, filename)) as t:
            try:
                self.browser.select_form(nr=0)            
                self.browser.find_control("doc").readonly = False
                self.browser.form.add_file(open(uploadFile, "rb"), "", filename)
                r = self.browser.submit()

                traffRec(wai(), fsize, False)                
                traffRec(wai(), len(r.read()))
            except: pass
            rec(wai(), t)
            
    def step_Search(self, criteria):
        with timed.measure("%s, Searching for '%s'."%(self.username, criteria)) as t:
            self.browser.open(self.up["URI_search"])
            try:
                self.browser.select_form(nr=0)
                self.browser['criteria'] = criteria
                r = self.browser.submit()
                
                traffRec(wai(), len(r.read()))
            except: pass
            rec(wai(), t)
    
    def step_Logout(self):
        with timed.measure("%s, is logging out."%(self.username)) as t:
            r = self.browser.open(self.up["URI_logout"])
            traffRec(wai(), len(r.read()))
            rec(wai(), t)
    
#-------------------------------------
    def run(self):
        loggedIn = False
        start = time.time()
        
        while not self.queue.empty():
            #Retrieve a file from the queue and add its size
            uploadFile = self.queue.get()
            
            #If not logged in, log in
            if not loggedIn:
                self.step_Login()
                loggedIn = True
            
            #Navigate to cabinet upload page
            self.step_Navigate("cabinet upload", self.up["URI_cabUpload"] + self.cabID)
            
            #Upload a document
            self.step_UploadFile(uploadFile)
            
            #Navigate to recent docs page
            self.step_Navigate("recent docs", self.up["URI_recentDocs"])
            
            #Navigate to search page
            self.step_Search(''.join([random.choice(letters) for b in xrange(0, random.randint(3,12))]))

            #Wrap up test
            if loggedIn and self.queue.empty():                
                self.step_Logout()

            #Finish steps for current file            
            self.queue.task_done()

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

#prints the statistics graph
def printStats(tresults):
    #text portion of the generated PDF file
    def getTextReport(tresults):
        rtn = ""
        rtn += "Test:%s, FINISHED with %s users on %s items in %0.2fs\n Finished@%s\n"%(
            tresults['TNAME'], tresults['USERS'], len(tresults['ITEMS']), tresults['TIME'], time.asctime())
        for step in serverDict.keys():
            rtn += "\n%25s, %d users."%(step, serverDict[step])
        rtn += "\n"
        for step in pDict.keys():
            c = pDict[step]
            rtn += "\n%25s, \tmin:%0.3fs \tavg:%0.3fs \tmax:%0.3fs"%(step, smin(c), savg(c), smax(c))
        rtn += "\n\nBandwidth accumulated\n"
        for step in trafficDict.keys():
            rtn += "\n%25s, \tdownload:%20s \tupload:%20s"%(step, conversions.convert_bytes(trafficDict[step]['download']), conversions.convert_bytes(trafficDict[step]['upload']))
        rtn += "\n\nKnown errors\n"
        for step in errorDict.keys():
            rtn += "\n%25s, count: %d"%(step, errorDict[step])
        return rtn

    def writeLog(tresults, tstamp):
        filename = tstamp + ".log"
        f = open("logs/" + filename, "w")
        f.write(tresults['TNAME'] + "\n")
        f.write(str(tresults['USERS']) + " users. \n")
        f.write("Items used: \n")
        for step in tresults['ITEMS']:
            f.write(step + "\n")
        f.close()

    #Prepare for printing graphs and PDF
    
    stamp = str(int(time.time())) + "_" + results['TNAME']
    
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
    
    stats = plt.figure()
    stats.text(.1,.3, getTextReport(tresults), fontsize=10)
    stats.savefig(pp, format='pdf')
    
    writeLog(tresults, stamp)
    pp.close()

if __name__ == "__main__":
    results = callTest(
        aaaTest,
        usrStart = 0,
        usrEnd = 450,
        usrChunk = 15,
        usrCycle = 30,
        totalFiles = glob.glob(r"C:\cygwin\home\bvandemerwe\www.ols11.com.nyud.net\dprine\Books\Epub books\*.*")[:750],
        userObject = users.ducotDrones,
        urlPack = urls.ducotURLpack)
    
    printStats(results)
    
    print "Cleaning up."