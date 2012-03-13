#!/usr/bin/env python
#
#   Template of a Iuxtra test
#
import unittest
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 

from common import login, users, urls

myTags = ["Version", "Document", "Listview", "Folder"]

class Versioning(unittest.TestCase): #Change
    def setUp(self):
        self.driver = webdriver.Ie()
        self.driver.implicitly_wait(7) 
        
    def test_ND00409_1(self):
        driver = self.driver
        self.assertTrue(login.login(driver, users.root, users.password))

        driver.find_element_by_tag_name("html").click()
        
        testFolder = "http://google.com"

        driver.get(testFolder)
        
        driver.find_element_by_tag_name("html").click()

        login.logout(driver)

        

    
    def tearDown(self):
        self.driver.close()

suite = unittest.TestLoader().loadTestsFromTestCase(Versioning) #Change

if __name__ == "__main__":
    print "Versioning Tests\n%s\n%s\n"%(', '.join(myTags), str("-"*70))
    unittest.TextTestRunner(verbosity=2).run(suite)
else:
    myCases = suite
    