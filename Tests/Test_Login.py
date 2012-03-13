#!/usr/bin/env python
#
#   Tests the login / logout functionality of the NetDocuments service
#

import unittest
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from common import login, users, urls

myTags = []

class LoginLogout(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Ie()
        
    def test_LoginLogout(self):
        driver = self.driver
        self.assertTrue(login.login(driver, users.root, users.password))
        self.assertTrue(login.logout(driver))
    
    def tearDown(self):
        self.driver.close()

suite = unittest.TestLoader().loadTestsFromTestCase(LoginLogout)
if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite)
else:
    myCases = suite
    