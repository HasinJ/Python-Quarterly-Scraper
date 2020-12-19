from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import csv
import time
import datetime
import json
import pandas as pd
import math
import os
import logging
import traceback
import sys
from config import config
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


class sqlQueries(config):
    def __init__(self):
        super().__init__()
        self.date = None #for inputting
        self.dateDotNotation = None #for scraping
        self.set = None
        self.selectedDate = None
        self.fullDate = None

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

            except self.MySQLdb._exceptions.IntegrityError:
                print(f'PC Number: {pcNumber} exists in database.')
                continue
        print('\n')

    def dateTBL(self):
        cursor = self.mydb.cursor()
        delete = 0
        month = self.selectedDate.strftime('%B') #December
        DOW = self.selectedDate.strftime('%a') #Wed
        day = self.selectedDate.strftime('%d') #31
        year = self.selectedDate.strftime('%Y') #2020
        dayofyear=int(self.selectedDate.strftime('%j')) #356
        print(self.date) #12/31/2020

        #leap year
        try:
            leapday = datetime.date(int(year),2,29)
            print("Leap year = yes")
            if (self.selectedDate==leapday):
                dayofyear=29.1
            elif(self.selectedDate>leapday):
                dayofyear-=1
        except ValueError:
            print("Leap year = no")

        sql = 'INSERT INTO DateTBL (`Date`,`DOW`,`TOD`,`Month`,`Day`,`Year`,`Day of Year`) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        values = [str(self.selectedDate.isoformat()),DOW,'',month,day,year,dayofyear]
        cursor.execute(sql,values)
        self.mydb.commit()
        cursor.close()

    def findDays(self):
        if self.set['days']>=0:
            self.set['start'] = get_past_date(f'{self.set["days"]} days ago', self.set['end'])
            return self.set

        if self.set['start']!='empty' and self.set["end"]!='empty':
            start = datetime.date(self.set['start']['year'], self.set['start']['month'], self.set['start']['day']).strftime('%j')
            end = datetime.date(self.set['end']['year'], self.set['end']['month'], self.set['end']['day']).strftime('%j')
            self.set['days'] = int(end) - int(start)
            self.set['start'] = get_past_date(f'{self.set["days"]} days ago', self.set['end'])
            return self.set

        if self.set['start']!='empty' and self.set["end"]=='empty':
            self.set['start'] = datetime.date(self.set['start']['year'], self.set['start']['month'], self.set['start']['day'])
            return self.set

        return self.set

    def chooseDay(self, manual="empty"):
        hour = int(datetime.datetime.now().strftime('%H'))

        if manual!="empty":
            self.selectedDate = manual

        elif hour >= 23: #the half of the day
            self.selectedDate = get_past_date('today')
            print("use today's date")

        elif hour < 23: #the other half of the day
            self.selectedDate = get_past_date('yesterday')
            print("use yesterday's date")

        if self.selectedDate>get_past_date('today'):
            sys.exit('Incorrect date argument')
            exit()

        self.date = self.selectedDate.strftime('%x') #local version of date 12/31/21
        self.date = self.date[:6] + self.selectedDate.strftime('%Y') #adds the year in full, "2021" instead of "21"
        self.fullDate = self.selectedDate.strftime('%c')
        self.dateDotNotation = self.date.replace('/', '.')


    def sqlFile(self, folder, file):
        cursor = self.mydb.cursor()

        destination = self.getDirectory() + fr'\Consumption Table Queries\{folder}\{file}'

        with open(destination) as f:
            sql=''
            while True:
                line = f.readline()
                if not line:
                    sql+=line.strip()
                    break
                sql+=line.strip() + ' '
            #print(sql) #checks sql
            cursor.execute(sql)

        self.mydb.commit()
        cursor.close()

    def deleteDayForItems(self):
        cursor = self.mydb.cursor()
        dirList = os.listdir(self.getDirectory() + fr'\Consumption Table Queries\Insert Queries')

        #for every file in directory
        for file in dirList:
            tableName = file.split(' ')[0]
            sql=fr'DELETE FROM {tableName} '
            destination = self.getDirectory() + fr'\Consumption Table Queries\Insert Queries\{file}'
            if os.path.exists(destination)==True:
                with open(destination) as f:
                    while True:
                        line = f.readline()
                        if not line:
                            sql+=line.strip()
                            break
                        sql+=line.strip() + ' '

                    sql=f"{sql} AND `Date` = '{dateSTR}'".replace('Item','ItemName')
                    #print(sql) #checks sql
                    cursor.execute(sql)
                    self.mydb.commit()
        sql=f"DELETE FROM LeftoversTBL WHERE `Date` = '{self.selectedDate}'"
        cursor.execute(sql)
        self.mydb.commit()
        cursor.close()

    def deleteDayForQuarter(self):
        cursor=self.mydb.cursor()
        sql=f"DELETE FROM QuarterlyHourTBL WHERE `Date`='{self.selectedDate}';"
        cursor.execute(sql)
        self.mydb.commit()
        cursor.close()

    def deleteDayForDigital(self):
        cursor=self.mydb.cursor()
        sql=f"DELETE FROM DigitalTBL WHERE `Date`='{self.selectedDate}';"
        cursor.execute(sql)
        self.mydb.commit()
        cursor.close()


    def quarterlyHourTBL(self,pcNumber,columns):
        import csv
        cursor = self.mydb.cursor()

        insert=f''
        values=f''
        for i in range(len(columns)):
            insert+=f'`{columns[i]}`,'
            values+=f'%s,'
        insert=insert.replace('%','Percent')
        sql=f'INSERT INTO QuarterlyHourTBL ({insert[:-1]}) VALUES ({values[:-1]})'

        csv_data = csv.reader(open(self.getDirectory() + fr'\Reports\Quarterly Hours\{pcNumber}\{self.dateDotNotation}dataframe.csv'))
        next(csv_data) #to ignore header
        for row in csv_data:
           cursor.execute(sql, row)
        self.mydb.commit()
        cursor.close()

    def digitalTBL(self,pcNumber,columns):
        import csv
        cursor = self.mydb.cursor()

        insert=f''
        values=f''
        for i in range(len(columns)):
            insert+=f'`{columns[i]}`,'
            values+=f'%s,'
        insert=insert.replace('%','Percent')
        sql=f'INSERT INTO DigitalTBL ({insert[:-1]}) VALUES ({values[:-1]})'
        csv_data = csv.reader(open(self.getDirectory() + fr'\Reports\DDaily Summaries\{pcNumber}\{self.dateDotNotation}dataframe.csv'))
        next(csv_data) #to ignore header
        for row in csv_data:
           cursor.execute(sql, row)
        self.mydb.commit()
        print("Data committed to database.")
        cursor.close()

    def productMixTBLs(self,pcNumber,columns):
        pass

class Radiant(config):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.main_page=None
        self.oddCount=0
        self.evenCount=0
        self.__pcNumbers = []
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

    def clickTaskOption(self,id):
        time.sleep(3)
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "MenuFrame")))
        self.driver.switch_to.frame(frame)
        self.setWait(self.driver,20) #needs to be set everytime driver changes

        category = self.getWait().until(EC.element_to_be_clickable((By.ID, id)))
        ActionChains(self.driver).move_to_element(category).click(category).perform()
        self.driver.switch_to.default_content()
        self.setWait(self.driver,5) #needs to be set everytime driver changes

        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "fraContent")))
        self.driver.switch_to.frame(frame)
        self.setWait(self.driver,5) #needs to be set everytime driver changes

        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "Frame2")))
        self.driver.switch_to.frame(frame)
        self.setWait(self.driver,5) #needs to be set everytime driver changes

    def clickPCOptions(self,id):
        self.setWait(self.driver,5) #needs to be set everytime driver changes
        button = self.getWait().until(EC.presence_of_element_located((By.ID, f"{id}")))
        ActionChains(self.driver).move_to_element(button).click(button).perform()
        time.sleep(2)
        self.main_page = switchHandle(self.driver)
        self.setWait(self.driver,5)
        time.sleep(1)

    def inputPCNumber(self,PC,id):
        print(f'\nPCNumber: {PC}')
        inputBox=self.getWait().until(EC.presence_of_element_located((By.ID, f'{id}')))
        inputBox.clear()
        inputBox.send_keys(PC)

    def click(self,id):
        run = self.getWait().until(EC.element_to_be_clickable((By.ID, f"{id}")))
        ActionChains(self.driver).move_to_element(run).click(run).perform()
        time.sleep(2)

    def inputDate(self,date,id):
        self.click(f'{id}')
        self.main_page=switchHandle(self.driver)
        self.setWait(self.driver,5) #needs to be set everytime driver changes
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, 'renderFrame'))) #frame inside the modal box
        self.driver.switch_to.frame(frame)
        self.setWait(self.driver,5) #needs to be set everytime driver changes
        time.sleep(5)
        dateBox = self.getWait().until(EC.presence_of_element_located((By.ID, 'calStartDay')))
        dateBox.clear()
        dateBox.send_keys(date)
        time.sleep(5)
        dateBox = self.getWait().until(EC.presence_of_element_located((By.ID, 'calEndDay')))
        dateBox.clear()
        dateBox.send_keys(date)
        self.click('waSaveClose')
        time.sleep(1)
        self.backToReportOptions()

    def backToReportOptions(self): #from popup
        #go back to previous screen/frame
        self.driver.switch_to.window(self.main_page)
        self.driver.switch_to.default_content()

        frame = self.getWait().until(EC.presence_of_element_located((By.ID, "fraContent"))) #stays the same in report options screen
        self.driver.switch_to.frame(frame)

        frame = self.getWait().until(EC.presence_of_element_located((By.ID, 'Frame2'))) #stays the same in report options screen
        self.driver.switch_to.frame(frame)
        print('Switched. \n')

    def handlePCNumbers(self):
        frame = self.getWait().until(EC.presence_of_element_located((By.ID, 'renderFrame'))) #frame inside the modal box
        self.driver.switch_to.frame(frame)
        self.setWait(self.driver,5)
        time.sleep(1)

        soup = BeautifulSoup(self.driver.page_source,'html.parser')
        table = soup.find(id="grdHierarchy")
        rows = table.findAll(True, {'class':['gridRowOdd', 'gridRowEven']})

        for index in range(len(rows)):
            dataCell = rows[index].find(class_='gridCell')

            if("Closed" in dataCell.text.strip()):
                continue

            self.__pcNumbers.insert(index, dataCell.text.strip())

        time.sleep(1)
        close = self.getWait().until(EC.presence_of_element_located((By.ID, 'waCancel')))
        ActionChains(self.driver).move_to_element(close).click(close).perform()
        time.sleep(1)
        self.backToReportOptions()
        return self.__pcNumbers

    def setWait(self,driver,time): #needs to be set everytime driver changes
        self.__wait = WebDriverWait(driver,time)

    def getWait(self):
        return self.__wait


class QuarterlyHour(Radiant): #can use parent variables by just calling it
    def __init__(self,driver):
        super().__init__(driver)

    #method override (other ones should be under radiant)
    def inputDate(self,date):
        time.sleep(2)
        dateBox = self.getWait().until(EC.element_to_be_clickable((By.ID, "calStartDate")))
        dateBox.clear()
        dateBox.send_keys(date)


class ConsumptionTables(Radiant):
    def __init__(self, driver):
        super().__init__(driver)

    def selectOrgType(self):
        dropdown = self.getWait().until(EC.element_to_be_clickable((By.ID, f"__selOrgUnit")))
        ActionChains(self.driver).move_to_element(dropdown).click(dropdown).perform()
        time.sleep(2)
        for i in range(3):
            dropdown.send_keys(Keys.DOWN)
            time.sleep(1)
        dropdown.send_keys(Keys.ENTER)
        time.sleep(1)


class DDailySummary(Radiant):
    def __init__(self,driver):
        super().__init__(driver)

class scrapeQuarterlyHour(QuarterlyHour):
    def __init__(self,driver,date,oddCount,evenCount):
        super().__init__(driver)
        self.__date = date
        self.oddCount=oddCount
        self.evenCount=evenCount
        self.data=[]
        self.columns=[]

    def scrape(self,html):
        soup = BeautifulSoup(html,'html.parser')
        self.data=[]

        #pc number
        table = soup.find(id="ReportHeader").find('div',attrs={'align':'left'})
        pcNumber=table.text.strip().split(" ")[2]

        table = soup.find_all(class_='TableStyle')
        #column names
        self.columns=table[0]
        self.columns=self.columns.select('.CellStyle')
        i=0
        for column in self.columns:
            self.columns[i]=column.text.strip().replace(' ','')
            i+=1
        #rows
        table=table[1]
        rows = table.findAll(True, {'class':['RowStyleData', 'RowStyleDataEven']})
        start='no'
        for row in rows:
            cell=dict()
            cell['PCNumber']=pcNumber
            cell['Date']=self.__date
            for i in range(len(self.columns)):
                field=row.select('.CellStyle')[i]
                if field['id']=='0':
                    text=field.text.strip()
                    if start=='no' and text!='04:00 AM':
                        print(f'{text} skipped')
                        break
                    elif text=='10:15 PM':
                        self.__date=self.__date.replace('/','.')
                        self.columns=['PCNumber','Date']+self.columns
                        self.dump(pcNumber)
                        return #end
                    cell[self.columns[0]]=text
                    continue
                start='yes'
                cell[self.columns[i]]=field['dval']
            if start =='yes':
                self.data.append(cell)

    def dump(self,pcNumber):
        #checks for folder existence
        directory=self.getDirectory()
        if os.path.isdir(directory + fr'\Reports\Quarterly Hours')==False:
            if os.path.isdir(directory + fr'\Reports')==False:
                os.mkdir(directory + fr'\Reports')
            os.mkdir(directory + fr'\Reports\Quarterly Hours')
            os.mkdir(directory + fr'\Reports\Quarterly Hours\{pcNumber}')
        elif os.path.isdir(directory + fr'\Reports\Quarterly Hours\{pcNumber}')==False:
            os.mkdir(directory + fr'\Reports\Quarterly Hours\{pcNumber}')

        #checks for .json existence
        directory=self.getDirectory() + fr'\Reports\Quarterly Hours\{pcNumber}\{self.__date}'
        with open(directory + 'Output.json','w') as f:
            json.dump(self.data,f)
        df = pd.read_json(open(directory + 'Output.json','r'))
        df.to_csv(directory + 'dataframe.csv', index=False, header=True)

class scrapeConsumptionTables(ConsumptionTables):
    def __init__(self,driver,date,oddCount,evenCount):
        super().__init__(driver)
        self.__date = date
        self.oddCount=oddCount
        self.evenCount=evenCount
        self.data=[]
        self.columns=[]

    def scrape(self,html):
        pass

    def dump(self,pcNumber):
        pass

class scrapeDDailySummary(DDailySummary):
    def __init__(self,driver,date,oddCount,evenCount):
        super().__init__(driver)
        self.__date = date.replace('/',".")
        self.oddCount = oddCount
        self.evenCount = evenCount
        self.data=[]
        self.columns=[]


    def scrape(self,html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html,'html.parser')
        self.data=[]

        #pc number
        table = soup.find(id="ReportHeader").find('div',attrs={'align':'left'})
        pcNumber=table.text.strip().split(" ")[2]

        #column names
        table = soup.find(id="id_dest_destinations").parent
        self.columns=table.select('.CellStyle')
        i=0 #to skip PCnumber and date but still add to data
        for column in self.columns:
            self.columns[i]=column.text.strip().replace(' ','').replace('%',"Percent")
            i+=1
        table = table.parent

        #rows
        table=table.find_next_sibling("tbody")
        rows = table.findAll(True, {'class':['RowStyleData', 'RowStyleDataEven']})

        for row in rows:
            cell = dict()
            cell['PCNumber']=pcNumber
            cell['Date']=self.__date
            for i in range(len(self.columns)):
                field=row.select('.CellStyle')[i]
                text = field.text.strip()
                text=text.replace('%','').replace('$','').replace(',','')
                cell[self.columns[i]] = text
            self.data.append(cell)
            self.dump(pcNumber)
        self.columns = ['PCNumber','Date'] + self.columns
        print("scrapped...\n")

    def dump(self,pcNumber):
        import json
        import pandas as pd
        import os
        from os import path

        #checks for folder existence
        directory=self.getDirectory()
        if os.path.isdir(directory + fr'\Reports\DDaily Summaries')==False:
            if os.path.isdir(directory + fr'\Reports')==False:
                os.mkdir(directory + fr'\Reports')
            os.mkdir(directory + fr'\Reports\DDaily Summaries')
            os.mkdir(directory + fr'\Reports\DDaily Summaries\{pcNumber}')
        elif os.path.isdir(directory + fr'\Reports\DDaily Summaries\{pcNumber}')==False:
            os.mkdir(directory + fr'\Reports\DDaily Summaries\{pcNumber}')

        #checks for .json existence
        directory=self.getDirectory() + fr'\Reports\DDaily Summaries\{pcNumber}\{self.__date}'
        with open(directory + 'Output.json','w') as f:
            json.dump(self.data,f)
        df = pd.read_json(open(directory + 'Output.json','r'))
        df.to_csv(directory + 'dataframe.csv', index=False, header=True)
        print("dumped...")


#polymorphism
def switchHandle(currentDriver): #to popup
    main_page = currentDriver.current_window_handle
    handles = currentDriver.window_handles

    print(f'\n{len(handles)} handles located... switching windows...')
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

def get_past_date(str_days_ago,end='empty'):
    if end!='empty': TODAY = datetime.date(end['year'], end['month'], end['day'])
    else: TODAY = datetime.date.today()
    splitted = str_days_ago.split()
    if len(splitted) == 1 and splitted[0].lower() == 'today':
        return TODAY
    elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
        date = TODAY - relativedelta(days=1)
        return date
    elif splitted[1].lower() in ['day', 'days', 'd']:
        date = TODAY - relativedelta(days=int(splitted[0]))
        return date
    else:
        return "Wrong Argument format"

def startingTimer():
    print('Starting program in...')
    for i in range(5):
        print(i+1)
        time.sleep(1)

def ExceptionHandler(type, value, tb):
    logger.exception("Type: {0}".format(str(type)))
    logger.exception("Error: {0}".format(str(value)))
    traceback_str = traceback.format_tb(tb)
    print("traceback:\n")
    for string in traceback_str:
        print(string)
    queries.sendEmail(queries)

def setLogger():
    global print, logger
    #logger
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    if os.path.isdir(queries.getDirectory() + fr'\Logs')==False:
            os.mkdir(queries.getDirectory() + fr'\Logs')
    logger.addHandler(logging.FileHandler(queries.getDirectory()+fr'\Logs\{queries.dateDotNotation}.txt', 'w'))
    print = logger.info

def runProductMixUnfinished():
    root = webdriver.Ie(r"C:\Program Files (x86)\IEDriver\IEDriverServer.exe")
    startingTimer()
    queries = sqlQueries()
    queries.chooseDay() #can also be used for one day format: dateTBL({'year':2020, 'month':2, 'day':2}) day and month shouldnt have zero

    try:
        queries.dateTBL()
    except queries.MySQLdb._exceptions.IntegrityError:
        print('Date exists, deleting quarters associated with it... (not really)')
        #queries.deleteDayForQuarter()
        print('Done \n')
    task=ConsumptionTables(root)
    task.login()
    task.clickTaskOption("Node_1018704_0")
    task.selectOrgType()
    task.clickPCOptions('__lufBusUnit_image')
    pcNumbers = task.handlePCNumbers()
    queries.storeTBL(pcNumbers)
    print(f'{pcNumbers[0]} is the first PC')
    task.inputPCNumber(pcNumbers[0],"__lufBusUnit")
    task.inputDate(queries.date,'lkupDates_image')
    task.click('wrLHSalesMixCon__AutoRunReport')
    task = scrapeConsumptionTables(task.driver,queries.date,task.oddCount,task.evenCount)
    task.scrape(task.driver.page_source)
    time.sleep(5)
    task.driver.quit()

def runQuarterlyHour(queries):
    root = webdriver.Ie(r"C:\Program Files (x86)\IEDriver\IEDriverServer.exe")
    startingTimer()
    task = QuarterlyHour(root)
    task.login()

    queries.chooseDay(queries.set['start'])
    setLogger()
    sys.excepthook = ExceptionHandler
    print(f'\n[{queries.date}]')
    try:
        queries.dateTBL()
    except queries.MySQLdb._exceptions.IntegrityError:
        print('Date exists, deleting quarters associated with it...')
        queries.deleteDayForQuarter()
        print('Done \n')

    task.clickTaskOption("Node_1018702_0")
    task.clickPCOptions('lookupSite_image')
    pcNumbers = task.handlePCNumbers()
    queries.storeTBL(pcNumbers)
    print(f'{pcNumbers[0]} is the first PC')
    task.inputPCNumber(pcNumbers[0],"lookupSite")
    task.inputDate(queries.date)
    task.click('wrqtr_hour_sales_activity__AutoRunReport')
    task = scrapeQuarterlyHour(task.driver,queries.date,task.oddCount,task.evenCount)
    task.scrape(task.driver.page_source)
    queries.quarterlyHourTBL(pcNumbers.pop(0),task.columns)
    for pcNumber in pcNumbers:
        task.click('wrqtr_hour_sales_activity__Options') #goes back to report options
        task.inputPCNumber(pcNumber,"lookupSite")
        task.click('wrqtr_hour_sales_activity__AutoRunReport')
        task.scrape(task.driver.page_source)
        queries.quarterlyHourTBL(pcNumber,task.columns)
    task.driver.quit()

def runDigital(queries):
    root = webdriver.Ie(r"C:\Program Files (x86)\IEDriver\IEDriverServer.exe")
    startingTimer()
    task = DDailySummary(root)
    task.login()

    queries.chooseDay(queries.set['start'])
    setLogger()
    sys.excepthook = ExceptionHandler
    print(f'\n[{queries.date}]')
    try:
        queries.dateTBL()
    except queries.MySQLdb._exceptions.IntegrityError:
        print('Date exists, deleting digital data associated with it...')
        queries.deleteDayForDigital()
        print('Done \n')

    task.clickTaskOption("Node_1018698_0")
    task.clickPCOptions('__lufBusUnit_image')
    pcNumbers = task.handlePCNumbers()
    queries.storeTBL(pcNumbers)
    print(f'{pcNumbers[0]} is the first PC')
    task.inputPCNumber(pcNumbers[0],"__lufBusUnit")
    task.inputDate(queries.date,'wlfTimePeriod_image')
    task.click('wrDailySummary__AutoRunReport')
    task = scrapeDDailySummary(task.driver,queries.date,task.oddCount,task.evenCount)
    task.scrape(task.driver.page_source)
    queries.digitalTBL(pcNumbers.pop(0),task.columns)
    for pcNumber in pcNumbers:
        task.click("wrDailySummary__Options")
        task.inputPCNumber(pcNumber,"__lufBusUnit")
        task.click('wrDailySummary__AutoRunReport')
        time.sleep(2)
        task.scrape(task.driver.page_source)
        queries.digitalTBL(pcNumber,task.columns)
    time.sleep(2)
    task.driver.quit()

if __name__=="__main__":
    global queries
    queries = sqlQueries()
    starting = 'empty' #{'year':2019, 'month':1, 'day':1} to select starting date
    ending = 'empty' #{'year':2019, 'month':1, 'day':1} to select ending date
    queries.set = {"start":starting, "end":ending, "days":-1}
    queries.set = queries.findDays()

    while queries.set['days']>=0:
        print(f'{queries.set["days"]} days')
        queries.set = queries.findDays()


        print('\nQuarterly Hour Reports')
        runQuarterlyHour(queries)


        """
        print('\nProduct Mix Reports')
        runProductMixUnfinished()
        """


        print('\nDunkin Daily Summary')
        runDigital(queries)


        if queries.set['days']-1==-1: exit()
        queries.set['days']-=1

    runQuarterlyHour(queries)
    """runProductMixUnfinished()"""
    runDigital(queries)
