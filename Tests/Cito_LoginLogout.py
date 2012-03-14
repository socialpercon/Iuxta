#!/usr/bin/env python

from common import urls, users, mechBrowser, conversions, timed
from common.whoami import whoami as wai

import threading, time, random
import glob, os, uuid, re

import Cito_Core as cc

tempFilesFolder = r"C:\Temp\Cito"
#-------------------------------------
class LoginLogout(threading.Thread):
    def __init__(self, browserObject, username, password, cabinetID, queue, urlp, ssInfo = {}):
        threading.Thread.__init__(self)
        
        self.up = urlp
        self.browser = browserObject.b
        self.username = username
        self.password = password
        self.cabID = cabinetID
        self.queue = queue
        
        self.timed = 0
        self.sizes = 0

    def step_Login(self):
        def getServer(page):
            return filter(lambda x: "Patents" in x, page.split("</span>"))[0].split("(")[-1].strip(")")
        
        with timed.measure('%s, Logging in to netdocuments.'%(self.username)) as t:
            r = self.browser.open(self.up["URI_home"])
            s = r.read()
            cc.traffRec(wai(), len(s))
            cc.recServ(getServer(s))
            
            self.browser.select_form(name='loginform')
            self.browser['username'] = 'nd.automated_keeper'
            self.browser['password'] = self.password
            r = self.browser.submit()
            
            cc.traffRec(wai(), len(r.read()))
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
            #Retrieve a file from the queue and add its size
            x = self.queue.get()
            
            #If not logged in, log in
            if not loggedIn:
                self.step_Login()
                loggedIn = True

            #Wrap up test
            if loggedIn:                
                self.step_Logout()
                loggedIn = False

            #Finish steps for current file            
            self.queue.task_done()


if __name__ == "__main__":
    results = cc.callTest(
        LoginLogout,
        usrStart = 1,
        usrEnd = 450,
        usrChunk = 2,
        usrCycle = 15,
        totalFiles = range(0, 2000),
        userObject = users.ducotDrones,
        urlPack = urls.ducotURLpack,
        spreadsheet = '')
    
    cc.printStats(results)