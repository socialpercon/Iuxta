#!/usr/bin/env python
#
#   Template of a Iuxtra test
#
import unittest
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from common import login, users, urls

myTags = []

class Template(unittest.TestCase): #Change
    def setUp(self):
        self.driver = webdriver.Ie()
        
    def test_Template(self): #Change
        driver = self.driver
        self.assertTrue(login.login(driver, users.root, users.password))
        self.assertTrue(login.logout(driver))
    
    def tearDown(self):
        self.driver.close()

suite = unittest.TestLoader().loadTestsFromTestCase(Template) #Change
if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
else:
    myCases = suite
    