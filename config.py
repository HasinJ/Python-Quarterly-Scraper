
class config():
    def __init__(self):
        import MySQLdb
        self.__radUser = StringVar()
        self.__radPass = StringVar()
        self.__directory = StringVar()

        self.__RDSHost = StringVar()
        self.__RDSUser = StringVar()
        self.__RDSPass = StringVar()
        self.__RDSDb = StringVar()

        self.MySQLdb = MySQLdb
        self.mydb = self.MySQLdb.connect(host = self.__RDSHost,
            user = self.__RDSUser,
            passwd = self.__RDSPass,
            db = self.__RDSDb)

    def logger(self,date,fullDate):
        import logging
        import os
        global print
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        logger = logging.getLogger()
        if os.path.isdir(self.__directory + fr'\Logs')==False:
                os.mkdir(self.__directory + fr'\Logs')
        logger.addHandler(logging.FileHandler(self.__directory+fr'\Logs\{date}.txt', 'a'))
        print = logger.info
        print(fr'[{fullDate}]')

    def getDirectory(self):
        return self.__directory

    def getRadUser(self):
        return self.__radUser

    def getRadPass(self):
        return self.__radPass
