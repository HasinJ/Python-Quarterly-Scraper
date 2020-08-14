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
from config import config
import MySQLdb
from os import path
from bs4 import BeautifulSoup

class sqlQueries(config):
    def __init__(self):
        super().__init__()
        self.mydb = MySQLdb.connect(host = self._RDSHost,
            user = self._RDSUser,
            passwd = self._RDSPass,
            db = self._RDSDb)


    def handlePCNumbers(self, currentDriver):
        wait = WebDriverWait(currentDriver, 3)
        pcNumbers = []
        frame = wait.until(EC.presence_of_element_located((By.ID, 'renderFrame'))) #frame inside the modal box
        currentDriver.switch_to.frame(frame)
        time.sleep(1)

        soup = BeautifulSoup(currentDriver.page_source,'html.parser')
        table = soup.find(id="grdHierarchy")
        rows = table.findAll(True, {'class':['gridRowOdd', 'gridRowEven']})

        for index in range(len(rows)):
            dataCell = rows[index].find(class_='gridCell')
            pcNumbers.insert(index, dataCell.text.strip())
        if len(rows) == len(pcNumbers):
            time.sleep(1) #it'll wait once the pcNumbers are saved into pcNumbers array

        for pcNumber in pcNumbers:
            try:
                cursor = self.mydb.cursor()
                sql=f'INSERT INTO storeTBL (`PCNumber`) VALUES ({pcNumber})'
                #print(sql)
                cursor.execute(sql)
                self.mydb.commit()
                cursor.close()

                print(f'PC Number: {pcNumber} inserted.')

            except MySQLdb._exceptions.IntegrityError:
                print(f'PC Number: {pcNumber} exists in database.')
                continue


class loginpage(config):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.main_page=None
        self.__wait = WebDriverWait(self.driver,3) #private

    def login(self):
        #login text input
        self.driver.get('https://adqsr.radiantenterprise.com/bin/orf.dll/PE.platformForms.login.select.1.ghtm')
        self.__wait.until(EC.presence_of_element_located((By.ID, "weMemberId"))).send_keys(self.getRadUser())
        self.__wait.until(EC.presence_of_element_located((By.ID, "pwd"))).send_keys(self.getRadPass())
        time.sleep(1)

        #continue
        self.__wait.until(EC.presence_of_element_located((By.ID, "waLogin"))).send_keys(Keys.ENTER)
        time.sleep(1)
        self.__wait.until(EC.presence_of_element_located((By.ID, "waContinue"))).send_keys(Keys.ENTER)
        time.sleep(1)

    def clickPCNumbers(self,id):
        self.setWait(self.driver,5) #needs to be set everytime driver changes
        button = self.getWait().until(EC.presence_of_element_located((By.ID, f"{id}")))
        ActionChains(self.driver).move_to_element(button).click(button).perform()
        time.sleep(2)
        self.main_page = switchHandle(self.driver)
        time.sleep(1)

    def setWait(self,driver,time): #needs to be set everytime driver changes
        self.__wait = WebDriverWait(driver,time)

    def getWait(self):
        return self.__wait

class QuarterlyHour(loginpage): #can use parent variables by just calling it
    def __init__(self,driver):
        super().__init__(driver)

    def clickQuarterlySales(self):
        time.sleep(3)
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "MenuFrame")))
        self.driver.switch_to.frame(frame)

        self.setWait(self.driver,20) #needs to be set everytime driver changes
        category = self.getWait().until(EC.element_to_be_clickable((By.ID, "Node_1018702_0")))
        ActionChains(self.driver).move_to_element(category).click(category).perform()
        self.driver.switch_to.default_content()

        self.setWait(self.driver,5) #needs to be set everytime driver changes
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "fraContent")))
        self.driver.switch_to.frame(frame)

        self.setWait(self.driver,5) #needs to be set everytime driver changes
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "Frame2")))
        self.driver.switch_to.frame(frame)


class DDailySummary(loginpage):
    def __init__(self,driver):
        super().__init__(driver)

#polymorphism
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
    queries = sqlQueries()

    task1 = QuarterlyHour(root)
    task1.login()
    task1.clickQuarterlySales()
    task1.clickPCNumbers('lookupSite_image')
    queries.handlePCNumbers(task1.driver)

    task1.driver.quit()
    exit()
