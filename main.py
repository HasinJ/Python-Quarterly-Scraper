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

class loginpage(config):
    def __init__(self, driver):
        self.driver = driver
        self.main_page=None
        self.__wait = WebDriverWait(self.driver,3) #private

    def login(self):
        #login text input
        self.driver.get('https://adqsr.radiantenterprise.com/bin/orf.dll/PE.platformForms.login.select.1.ghtm')
        self.__wait.until(EC.presence_of_element_located((By.ID, "weMemberId"))).send_keys(config.radUser)
        self.__wait.until(EC.presence_of_element_located((By.ID, "pwd"))).send_keys(config.radPass)
        time.sleep(1)

        #continue
        self.__wait.until(EC.presence_of_element_located((By.ID, "waLogin"))).send_keys(Keys.ENTER)
        time.sleep(1)
        self.__wait.until(EC.presence_of_element_located((By.ID, "waContinue"))).send_keys(Keys.ENTER)
        time.sleep(1)

    def setWait(self,driver,time): #needs to be set everytime driver changes
        self.__wait = WebDriverWait(driver,time)

    def getWait(self):
        return self.__wait


class QuarterlyHour(loginpage): #can use parent variables by just calling it
    def __init__(self,driver):
        super().__init__(driver)
        self.clickQuarterlySales()
        self.clickPCNumbers()
        self.driver.quit()

    def clickQuarterlySales(self):
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "MenuFrame")))
        self.driver.switch_to.frame(frame)

        self.setWait(self.driver,20) #needs to be set everytime driver changes
        report = self.getWait().until(EC.element_to_be_clickable((By.ID, "Node_1018702_0")))
        ActionChains(self.driver).move_to_element(report).click(report).perform()
        self.driver.switch_to.default_content()

        self.setWait(self.driver,5)
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "fraContent")))
        self.driver.switch_to.frame(frame)

        self.setWait(self.driver,5)
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "Frame2")))
        self.driver.switch_to.frame(frame)

    def clickPCNumbers(self):
        self.setWait(self.driver,5)
        button = self.getWait().until(EC.presence_of_element_located((By.ID, "lookupSite_image")))
        ActionChains(self.driver).move_to_element(button).click(button).perform()
        time.sleep(2)
        self.main_page = switchHandle(self.driver)


class DDailySummary(loginpage):
    def __init__(self,driver):
        super().__init__(driver)
        self.driver.quit()

class PCNumbersIntoDatabase():
    def __init__(self, driver):
        hurrdurr='hurrdurr'




def switchHandle(currentDriver): #to popup
    main_page = currentDriver.current_window_handle
    handles = currentDriver.window_handles

    print(f'{len(handles)} handles located... switching windows...')
    popup_window_handle = None

    # loop through the window handles and find the popup window.
    for handle in currentDriver.window_handles:
        if handle != main_page:
            popup_window_handle = handle
            break

    # switch to the popup window.
    currentDriver.switch_to.window(popup_window_handle)
    return main_page

def backToReportOptions(currentDriver, main_page, wait, frameID='Frame2', closeID='nothing'): #from popup
    print('Switching driver focus back to report options...')

    #click on save and close
    if closeID != 'nothing':
        wait = WebDriverWait(currentDriver,waitingTime)
        saveANDclose = wait.until(EC.presence_of_element_located((By.ID, closeID)))
        saveANDclose.send_keys(Keys.ENTER)

    #go back to previous screen/frame
    currentDriver.switch_to.window(main_page)
    currentDriver.switch_to.default_content()

    frame = wait.until(EC.presence_of_element_located((By.ID, "fraContent"))) #stays the same in report options screen
    currentDriver.switch_to.frame(frame)

    frame = wait.until(EC.presence_of_element_located((By.ID, f"{frameID}"))) #stays the same in report options screen
    currentDriver.switch_to.frame(frame)

if __name__=="__main__":
    root = webdriver.Ie(r"C:\Program Files (x86)\IEDriver\IEDriverServer.exe")
    QuarterlyHour(root)
    exit()
