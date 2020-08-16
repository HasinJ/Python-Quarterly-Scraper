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


    def storeTBL(self, pcNumbers):
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
        print('\n')


class Radiant(config):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.main_page=None
        self.odd=None
        self.even=None
        self.oddCount=int()
        self.evenCount=int()
        self.pcNumbers = []
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

    def clickPCOptions(self,id):
        self.setWait(self.driver,5) #needs to be set everytime driver changes
        button = self.getWait().until(EC.presence_of_element_located((By.ID, f"{id}")))
        ActionChains(self.driver).move_to_element(button).click(button).perform()
        time.sleep(2)
        self.main_page = switchHandle(self.driver)
        time.sleep(1)

    def clickFirstPC(self):
        firstPC=None
        self.odd = self.driver.find_elements_by_class_name('gridRowOdd')
        self.even = self.driver.find_elements_by_class_name('gridRowEven')
        elements = self.even + self.odd #for selenium to click
        time.sleep(1)

        for elementsIndex in range(len(elements)):
            somePC = elements[elementsIndex].find_element_by_class_name('gridCell').find_element_by_tag_name('span').get_attribute("innerHTML")
            if somePC != self.pcNumbers[0]:
                continue
            elif somePC == self.pcNumbers[0]:
                firstPC = elements[elementsIndex]
                print(f'\n{somePC} is the first PC number AKA Business Unit')
                self.pcNumbers.remove(somePC)
                self.oddCount = 1
                break

        ActionChains(self.driver).move_to_element(firstPC).click(firstPC).perform()
        time.sleep(1)
        self.backToReportOptions()

    def backToReportOptions(self, **kwargs): #from popup
        print('Switching driver focus back to report options...')

        #click on save and close
        for key, value in kwargs.items():
            if key == 'closeID':
                setWait(self.driver, 5)
                saveANDclose = self.getWait().until(EC.presence_of_element_located((By.ID, closeID)))
                saveANDclose.send_keys(Keys.ENTER)
                break
            elif len(kwargs) > 1:
                print('too many arguments for backToReportOptions()')
                self.driver.quit()
                exit()

        #go back to previous screen/frame
        self.driver.switch_to.window(self.main_page)
        self.driver.switch_to.default_content()

        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "fraContent"))) #stays the same in report options screen
        self.driver.switch_to.frame(frame)

        frame = self.getWait().until(EC.presence_of_element_located((By.ID, 'Frame2'))) #stays the same in report options screen
        self.driver.switch_to.frame(frame)
        print('Switched. \n')
        print(self.driver.page_source)

    def handlePCNumbers(self):
        wait = WebDriverWait(self.driver, 3)
        frame = wait.until(EC.presence_of_element_located((By.ID, 'renderFrame'))) #frame inside the modal box
        self.driver.switch_to.frame(frame)
        time.sleep(1)

        soup = BeautifulSoup(self.driver.page_source,'html.parser')
        table = soup.find(id="grdHierarchy")
        rows = table.findAll(True, {'class':['gridRowOdd', 'gridRowEven']})

        for index in range(len(rows)):
            dataCell = rows[index].find(class_='gridCell')
            self.pcNumbers.insert(index, dataCell.text.strip())
        if len(rows) == len(self.pcNumbers):
            time.sleep(1) #it'll wait once the pcNumbers are saved into pcNumbers array

    def setWait(self,driver,time): #needs to be set everytime driver changes
        self.__wait = WebDriverWait(driver,time)

    def getWait(self):
        return self.__wait


class QuarterlyHour(Radiant): #can use parent variables by just calling it
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
        self.setWait(self.driver,5) #needs to be set everytime driver changes


class DDailySummary(Radiant):
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
    print('Switched. \n')
    return main_page

def get_past_date(str_days_ago):
    TODAY = datetime.date.today()
    splitted = str_days_ago.split()
    if len(splitted) == 1 and splitted[0].lower() == 'today':
        return TODAY
    elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
        date = TODAY - relativedelta(days=1)
        return date
    else:
        return "Wrong Argument format"


if __name__=="__main__":
    root = webdriver.Ie(r"C:\Program Files (x86)\IEDriver\IEDriverServer.exe")
    queries = sqlQueries()

    task1 = QuarterlyHour(root)
    task1.login()
    task1.clickQuarterlySales()
    task1.clickPCOptions('lookupSite_image')
    task1.handlePCNumbers()
    queries.storeTBL(task1.pcNumbers)
    task1.clickFirstPC()

    task1.driver.quit()
    exit()
