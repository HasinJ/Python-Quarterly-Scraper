class scrapeQuarterlyHour():
    def __init__(self):
        #self._html = driver.page_source'
        self._html = open(fr'C:\Users\Hasin Choudhury\Desktop\pythonQuarterlyHour' + fr'\report.html','rb') # 'rb' stands for read-binary, write-binary needs chmoding, this also needs to be changed for Selenium (needs to have date)
        #self._date = date
        print('the commented line above this needs to be figured out')

    #this is the part that needs to be copied
    def scrape(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self._html,'html.parser')
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
            for i in range(len(columnNames)):
                field=row.select('.CellStyle')[i]
                if field['id']=='0':
                    if start=='no' and field.text.strip()!='05:00 AM':
                        print(field.text.strip() + ' skipped')
                        break
                    continue #placeholder
                start='yes'
                print(field)
                #print(row)
                #print(row.select('.CellStyle')[0])
                #print(row.findAll(True, {'class':['CellStyle']})[1].attrs['dval'])
        #print(rows[0].select('.CellStyle')[1].attrs['dval'])

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
