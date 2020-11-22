
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

        self.__sender_email = StringVar() # Enter your address
        self.__receiver_email = StringVar()  # Enter receiver address
        self.__password = StringVar()

        self.MySQLdb = MySQLdb
        self.mydb = self.MySQLdb.connect(host = self.__RDSHost,
            user = self.__RDSUser,
            passwd = self.__RDSPass,
            db = self.__RDSDb)

    def getDirectory(self):
        return self.__directory

    def getRadUser(self):
        return self.__radUser

    def getRadPass(self):
        return self.__radPass

    def sendEmail(self, queries):
        import smtplib, ssl

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        message = f"""\
        Subject: Error in Application

        Automation application has thrown an error. Please check logs for {queries.date}.

        DO NOT REPLY."""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(self.__sender_email, self.__password)
            server.sendmail(self.__sender_email, self.__receiver_email, message)
