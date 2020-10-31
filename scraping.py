class scrapeQuarterlyHour():
    def __init__(self):
        #self._html = driver.page_source'
        self._html = open(fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour' + fr'\report.html','rb') # 'rb' stands for read-binary, write-binary needs chmoding, this also needs to be changed for Selenium (needs to have date)
        self.data=[]
        self.columns=[]
        self.__date='8.19.2020'
        print('the commented line above this needs to be figured out')

    #this is the part that needs to be copied
    def scrape(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self._html,'html.parser')
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
                        return
                    cell[self.columns[0]]=text
                    continue
                start='yes'
                cell[self.columns[i]]=field['dval']
            if start =='yes':
                self.data.append(cell)

    def dump(self,pcNumber):
        import json
        import pandas as pd
        import os
        from os import path

        #checks for folder existence
        directory=fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour'
        if path.isdir(directory + fr'\Reports\Quarterly Hours')==False:
            if path.isdir(directory + fr'\Reports')==False:
                os.mkdir(directory + fr'\Reports')
            os.mkdir(directory + fr'\Reports\Quarterly Hours')
            os.mkdir(directory + fr'\Reports\Quarterly Hours\{pcNumber}')

        #checks for .json existence
        directory=fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour\Reports\Quarterly Hours\{pcNumber}\{self.__date}'
        if path.exists(directory + 'Output.json')==False:
            with open(directory + 'Output.json','w') as f:
                json.dump(self.data,f)
            df = pd.read_json(open(directory + 'Output.json','r'))
            df.to_csv(directory + 'dataframe.csv', index=False, header=True)


class scrapeDDailySummary():
    def __init__(self):
        #super().__init__(driver)
        #self.__date = date
        #self.oddCount=oddCount
        #self.evenCount=evenCount
        #self.data=[]
        #self.columns=[]
        self._html = open(fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour' + fr'\reportDDaily.html','rb') # 'rb' stands for read-binary, write-binary needs chmoding, this also needs to be changed for Selenium (needs to have date)
        self.data=[]
        self.columns=[]
        self.__date='10.30.2020'

    def scrape(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self._html,'html.parser')
        self.data=[]

        #pc number
        table = soup.find(id="ReportHeader").find('div',attrs={'align':'left'})
        pcNumber=table.text.strip().split(" ")[2]
        print(pcNumber);

        #column names
        table = soup.find(id="id_dest_destinations").parent
        self.columns=table.select('.CellStyle')
        i=0
        for column in self.columns:
            self.columns[i]=column.text.strip().replace(' ','')
            i+=1
        table = table.parent

        print(self.columns)

        #rows
        table=table.find_next_sibling("tbody")
        rows = table.findAll(True, {'class':['RowStyleData', 'RowStyleDataEven']})
        print(rows[1])




    def dump(self,pcNumber):
        pass

"""
test = scrapeQuarterlyHour()
test.scrape()
print(test.columns)

insert=f''
values=f''
for i in range(len(test.columns)):
    insert+=f'`{test.columns[i]}`,'
    values+=f'%s,'
insert=insert.replace('%','Percent')
sql=f'INSERT INTO QuarterlyHourTBL ({insert[:-1]}) VALUES ({values[:-1]})'
print(sql)
['TimePeriodBegins', 'NetSales', 'TransCount', 'EstimatedLaborCost', 'LaborHours', 'LaborCost%NetSales', 'NetSales/LaborHour', 'Trans/LaborHour']
"""

test = scrapeDDailySummary()
test.scrape()
