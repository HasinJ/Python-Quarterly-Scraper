class config():
    def __init__(self):
        self.__radUser = StringVar()
        self.__radPass = StringVar()
        self.__directory = StringVar()
        self._RDSHost = StringVar()
        self._RDSUser = StringVar()
        self._RDSPass = StringVar()
        self._RDSDb = StringVar()

    def getDirectory(self):
        return self.directory

    def getRadUser(self):
        return self.__radUser

    def getRadPass(self):
        return self.__radPass
