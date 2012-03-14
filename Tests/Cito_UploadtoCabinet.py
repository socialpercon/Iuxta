#!/usr/bin/env python

from common import urls, users, mechBrowser, conversions, timed
from common.whoami import whoami as wai

import threading, time, random
import glob, os, uuid, re

import Cito_Core as cc

tempFilesFolder = r"C:\Temp\Cito"
#-------------------------------------
class UploadFilestoCabinet(threading.Thread):
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
            self.browser['username'] = self.username
            self.browser['password'] = self.password
            r = self.browser.submit()
            
            cc.traffRec(wai(), len(r.read()))
            cc.rec(wai(), t)
    
    def step_NavigateCabinetUpload(self):
        with timed.measure("%s, is navigating to cabinet upload page."%(self.username)) as t:
            r = self.browser.open(self.up["URI_cabUpload"] + self.cabID)
            
            cc.traffRec(wai(), len(r.read()))
            cc.rec(wai(), t)
        
    def step_UploadFile(self, uploadFile):
        filename = uploadFile.split("\\")[-1]
        fsize = int(os.path.getsize(uploadFile))
        with timed.measure('%s, Uploading file %s.'%(self.username, filename)) as t:
            try:
                self.browser.select_form(nr=0)            
                self.browser.find_control("doc").readonly = False
                self.browser.form.add_file(open(uploadFile, "rb"), "", filename)
                r = self.browser.submit()

                cc.traffRec(wai(), fsize, False) #record to upload traffic
                cc.traffRec(wai(), len(r.read()))
            except: pass
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
            uploadFile = self.queue.get()
            
            #If not logged in, log in
            if not loggedIn:
                self.step_Login()
                loggedIn = True

            self.step_NavigateCabinetUpload()
            
            self.step_UploadFile(uploadFile)

            #Wrap up test
            if loggedIn and self.queue.empty():                
                self.step_Logout()
                loggedIn = False

            #Finish steps for current file            
            self.queue.task_done()


if __name__ == "__main__":
    results = cc.callTest(
        UploadFilestoCabinet,
        usrStart = 250,
        usrEnd = 470,
        usrChunk = 15,
        usrCycle = 7,
        totalFiles = glob.glob(r"C:\cygwin\home\bvandemerwe\www.ols11.com.nyud.net\dprine\Books\Epub books\*.*")[:450],
        userObject = users.ducotDrones,
        urlPack = urls.ducotURLpack,
        spreadsheet = '')
    
    cc.printStats(results)