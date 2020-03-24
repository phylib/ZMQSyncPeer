import os

class Logger:
    def __init__(self, logDir):
        self.logDir = logDir
        self.logFile = open(logDir+"\\changeLog.txt", "w");

    def initFile(self):
        self.logFile.write("Hello there!\n");
        print("Logfile-Path: %s" %os.path.abspath(self.logFile.name))
        self.logFile.close()