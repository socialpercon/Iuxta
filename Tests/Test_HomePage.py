#!/usr/bin/env python
#
#   Tests the home page of ducot.NetDocuments.com
#

import unittest
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from common import login, users, urls, navpane, homepage


myTags = []

class HomePage(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Ie()
        
    def test_HomePage(self):
        driver = self.driver
        self.assertTrue(login.login(driver, "bvandemerwea", users.password))

        driver.get(urls.home)
        
        a = driver.find_element_by_link_text("Customize Layout")
        a.click()
                
        time.sleep(2)
        a = driver.find_element_by_link_text("Cancel")
        a.click()
                
        self.assertTrue(login.logout(driver))
    
    def tearDown(self):
        self.driver.close()

suite = unittest.TestLoader().loadTestsFromTestCase(HomePage) # Change
if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
else:
    myCases = suite
    