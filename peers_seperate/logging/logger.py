import os

class Logger:
    def __init__(self, logDir):
        self.logDir = logDir
        self.logFile = open(logDir+"\\changeLog.txt", "w");

    '''def initFile(self):
        self.logFile.write("Hello there!\n");
        print("Logfile-Path: %s" %os.path.abspath(self.logFile.name))
        self.logFile.close()'''

    def logChunkUpdateProduced(self, chunk, timestamp):
        self.logFile.write("%s\tOUT\t%d\t%d\t%d\n" %(timestamp, chunk.x, chunk.y, chunk.data))

    def closeFile(self):
        self.logFile.close()