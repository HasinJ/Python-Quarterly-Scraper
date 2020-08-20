class scrapeQuarterlyHour():
    def __init__(self):
        #self._html = driver.page_source'
        self._html = open(fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour' + fr'\report.html','rb') # 'rb' stands for read-binary, write-binary needs chmoding, this also needs to be changed for Selenium (needs to have date)
        self.data=[]
        self.dateDotNotation='8.19.2020'
        print('the commented line above this needs to be figured out')

    #this is the part that needs to be copied
    def scrape(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self._html,'html.parser')

        #pc number
        table = soup.find(id="ReportHeader").find('div',attrs={'align':'left'})
        pcNumber=table.text.strip().split(" ")[2]

        table = soup.find_all(class_='TableStyle')
        #column names
        columnNames=table[0]
        columnNames=columnNames.select('.CellStyle')
        i=0
        for column in columnNames:
            columnNames[i]=column.text.strip()
            i+=1
        #rows
        table=table[1]
        rows = table.findAll(True, {'class':['RowStyleData', 'RowStyleDataEven']})
        start='no'
        for row in rows:
            cell=dict()
            for i in range(len(columnNames)):
                field=row.select('.CellStyle')[i]
                if field['id']=='0':
                    text=field.text.strip()
                    if start=='no' and text!='04:00 AM':
                        #print(text + ' skipped')
                        break
                    elif text=='10:15 PM':
                        self.dump(pcNumber)
                        return
                    cell[columnNames[0]]=text
                    continue
                start='yes'
                cell[columnNames[i]]=field['dval']
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
        directory=fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour\Reports\Quarterly Hours\{pcNumber}\{self.dateDotNotation}'
        if path.exists(directory + 'Output.json')==False:
            with open(directory + 'Output.json','w') as f:
                json.dump(self.data,f)
            df = pd.read_json(open(directory + 'Output.json','r'))
            df.to_csv(directory + 'dataframe.csv', index=False, header=True)


class scrapeDDailySummary():
    def __init__(self):
        #self._html = driver.page_source'
        self._html = open(fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour' + fr'\report.html','rb') # 'rb' stands for read-binary, write-binary needs chmoding, this also needs to be changed for Selenium (needs to have date)
        #self._date = date
        print('the commented line above this needs to be figured out')

    def scrape(self):
        from bs4 import BeautifulSoup
        pass

test = scrapeQuarterlyHour()
test.scrape()