#!/usr/bin/env python

from common import urls, users, mechBrowser, conversions, timed
from common.whoami import whoami as wai

import threading, time, random
import glob, os, uuid, re

import Cito_Core as cc

tempFilesFolder = r"C:\Temp\Cito"
#-------------------------------------
class DownloadFile(threading.Thread):
    def __init__(self, browserObject, username, password, cabinetID, queue, urlp, ssInfo = {}):
        threading.Thread.__init__(self)
        
        self.up = urlp
        self.browser = browserObject.b
        self.username = username
        self.password = password
        self.cabID = cabinetID
        self.queue = queue
        self.ssInfo = ssInfo
        self.ssHeader = self.ssInfo[-1]
        
        self.timed = 0
        self.sizes = 0
        
        self.ssInfo.pop()
        
    def step_Login(self):
        def getServer(page):
            return filter(lambda x: "Patents" in x, page.split("</span>"))[0].split("(")[-1].strip(")")
        
        with timed.measure('%s, Logging in to netdocuments.'%(self.username)) as t:
            r = self.browser.open(self.up["URI_home"])
            s = r.read()
            cc.traffRec(wai(), len(s))
            cc.recServ(getServer(s))
            
            self.browser.select_form(name='loginform')
            self.browser['username'] = self.username
            self.browser['password'] = self.password
            r = self.browser.submit()
            
            cc.traffRec(wai(), len(r.read()))
            cc.rec(wai(), t)
    
    def step_NavigateSearch(self):
        with timed.measure("%s, is navigating to search page."%(self.username)) as t:
            r = self.browser.click_link(text="Search")
            s = self.browser.open(r)
            
            cc.traffRec(wai(), len(s.read()))
            cc.rec(wai(), t)
    
    def step_SearchForFolder(self):
        with timed.measure("%s, is searching for root folder."%(self.username)) as t:
            self.browser.select_form(nr=0)
            self.browser['criteria'] = self.ssInfo[0][self.ssHeader.index('FOLDER')]
            r = self.browser.submit()

            cc.traffRec(wai(), len(r.read()))
            cc.rec(wai(), t)
    
    def step_NavigateRootFolder(self):
        with timed.measure("%s, is navigating to root folder."%(self.username)) as t:
            try:
                r = self.browser.click_link(text=self.ssInfo[0][self.ssHeader.index('FOLDER')])
                s = self.browser.open(r)
                
                cc.traffRec(wai(), len(s.read()))
            except: cc.errorRec("Couldn't find root folder in search results.")
            
            cc.rec(wai(), t)
    
    def step_NavigateDocumentProfile(self):
        line = random.choice(self.ssInfo)
        doc = line[self.ssHeader.index('DOCUMENT NAME')]
        with timed.measure('%s, is navigating to %s profile page.'%(self.username, doc)) as t:
            try:
                r = self.browser.click_link(text=doc)
                s = self.browser.open(r)
                
                cc.traffRec(wai(), len(s.rread()))
            except: cc.errorRec("%s couldn't find expected document."%(self.username))
    
            cc.rec(wai(), t)
    
    def step_DownloadDocument(self):
        with timed.measure('%s, is downloading document.'%(self.username)) as t:
            try:
                #determine file extension listed on the current page
                fileExtension = re.search('File extension:</span> <b>.(\w+)</b>', self.browser.response().read()).groups()[0]
                
                r = self.browser.click_link(text='Download')
                self.browser.open(r)
                a = self.browser.response().read()
    
                cc.traffRec(wai(), len(a))
                
                with open('%s\\%s.%s'%(tempFilesFolder, str(uuid.uuid4()), fileExtension), 'wb') as f:
                    f.write(a)    
            except: cc.errorRec("%s couldn't find download link in doc profile."%(self.username))
            
            cc.rec(wai(), t)
    
    
    def step_Logout(self):
        with timed.measure("%s, is logging out."%(self.username)) as t:
            r = self.browser.open(self.up["URI_logout"])
            
            cc.traffRec(wai(), len(r.read()))
            cc.rec(wai(), t)
    
#-------------------------------------
    def run(self):
        loggedIn = False
        start = time.time()
        
        while not self.queue.empty():
            #Retrieve a file from the queue
            x = self.queue.get()
            
            #If not logged in, log in
            if not loggedIn:
                self.step_Login()
                loggedIn = True

            self.step_NavigateSearch()
            
            self.step_SearchForFolder()

            self.step_NavigateRootFolder()
            
            self.step_NavigateDocumentProfile()
            
            self.step_DownloadDocument()

            #Wrap up test
            if loggedIn:                
                self.step_Logout()
                loggedIn = False

            #Finish steps for current file            
            self.queue.task_done()


if __name__ == "__main__":
    results = cc.callTest(
        DownloadFile,
        usrStart = 670,
        usrEnd = 950,
        usrChunk = 45,
        usrCycle = 18,
        totalFiles = range(0, 550),
        userObject = users.ducotDrones,
        urlPack = urls.ducotURLpack,
        spreadsheet = r'C:\Users\bvandemerwe.NV\Documents\My Dropbox\NetDocuments\Automated\csvs\cito_fileupload-1330709380.csv')
    
    cc.printStats(results)