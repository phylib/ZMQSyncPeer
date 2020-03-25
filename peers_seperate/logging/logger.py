import threading
import os
class Logger:
    def __init__(self, logDir):
        self.logDir = logDir
        if(not(os.path.exists(self.logDir))):
            os.makedirs(self.logDir)
        self.logFile = open(logDir+"/changeLog.txt", "w");
        self.lock = threading.Lock();

    def logChunkUpdateProduced(self, chunk, timestamp):
        self.lock.acquire()
        self.logFile.write("%s\tOUT\t%d\t%d\t%d\n" %(timestamp, chunk.x, chunk.y, chunk.data))
        self.lock.release()

    def logChunkUpdateReceived(self, chunk, timestamp):
        self.lock.acquire()
        self.logFile.write("%s\tIN\t%d\t%d\t%d\n" %(timestamp, chunk.x, chunk.y, chunk.data))
        self.lock.release()

    def closeFile(self):
        self.logFile.close()