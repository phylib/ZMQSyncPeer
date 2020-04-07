import threading
import os

class Logger:
    """
    The Logger class is responsible for logging
    changes in a logfile.

    The logger is also part of the peer
    and logs the sent updates of the server as well
    as the received updates of the clients in the same logfile.
    The server updates are marked with an OUT-tag to represent
    it as an outgoing update. The clients' log entries
    are marked with an IN-tag to represent it
    as an incoming update.
    """
    def __init__(self, logDir, logFileName):
        """
        Initializes the logger.
        :param logDir: the path to the directory in which the logfile should be saved
        :type logDir: str
        """
        self.logDir = logDir
        if(not(os.path.exists(self.logDir))):
            os.makedirs(self.logDir)
        self.logFile = open("{}/{}".format(logDir, logFileName), "w")
        self.lock = threading.Lock()

    def logChunkUpdateProduced(self, chunk, timestamp, numChanges):
        """
        This is the logging method for the server.

        When the server wants to write its published update
        in the logfile the file has to be locked.
        If the server is done with the write operation
        the lock is released.
        :param chunk: one coordinate pair of the update
        :type chunk: Chunk
        :param timestamp: the time at which the server sent the update
        :type timestamp: time
        :param numChanges: the number of changed coordinates in the current update
        :type numChanges: int
        """
        self.lock.acquire()
        self.logFile.write("%s\tOUT\t%d\t%d\t%d\t%d\n" %(timestamp, chunk.x, chunk.y, chunk.data, numChanges))
        self.lock.release()

    def logChunkUpdateReceived(self, chunk, timestamp):
        """
        This is the logging method for the client.

        When the client wants to write its received update
        in the logfile the file has to be locked.
        If the client is done with the write operation
        the lock is released.
        :param chunk: one coordinate pair of the update
        :type chunk: Chunk
        :param timestamp: the time at which the client received the update
        :type timestamp: time
        """
        self.lock.acquire()
        self.logFile.write("%s\tIN\t%d\t%d\t%d\t\n" %(timestamp, chunk.x, chunk.y, chunk.data))
        self.lock.release()

    def closeFile(self):
        """
        When the peer of which the logger is part of
        shuts down the logfile has to be closed.
        """
        self.logFile.close()