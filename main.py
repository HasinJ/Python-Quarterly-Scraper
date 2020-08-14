from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import json
import pandas as pd
import os.path
import csv
import time
import config
from os import path
from bs4 import BeautifulSoup


class loginpage():
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver,3)
        self.driver.get('https://adqsr.radiantenterprise.com/bin/orf.dll/PE.platformForms.login.select.1.ghtm')
        self.login()
        self.driver.quit()

    def login(self):
        #login text input
        self.wait.until(EC.presence_of_element_located((By.ID, "weMemberId"))).send_keys(config.radUser)
        self.wait.until(EC.presence_of_element_located((By.ID, "pwd"))).send_keys(config.radPass)
        time.sleep(1)

        #continue
        self.wait.until(EC.presence_of_element_located((By.ID, "waLogin"))).send_keys(Keys.ENTER)
        time.sleep(1)
        self.wait.until(EC.presence_of_element_located((By.ID, "waContinue"))).send_keys(Keys.ENTER)
        time.sleep(1)



if __name__=="__main__":
    root = webdriver.Ie(r"C:\Program Files (x86)\IEDriver\IEDriverServer.exe")
    loginpage(root)
    exit()
