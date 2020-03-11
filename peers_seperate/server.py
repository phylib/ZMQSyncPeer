#
#   Weather update server
#   Binds PUB socket to tcp://*:5556
#   Publishes random weather updates
#

import zmq
from random import randrange
import threading
import time


class Server (threading.Thread):

    def __init__(self, port, peer=None):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port
        self.peer = peer
        self.socket.bind("tcp://*:%d" %(self.port))
        threading.Thread.__init__(self)


    def run(self):
        count = 0
        logfile = open("ChunkChanges-very-distributed.csv", "r")
        line = logfile.readline()

        while count < 20:
            self.socket.send_string(str(self.port) + " " +line)
            print("[localhost:%d]: sent update %d %s" %(self.port, self.port, line))
            line = logfile.readline()
            count += 1
            time.sleep(0.5)  # set to 0.5

        logfile.close()

        if(self.peer != None):
            print("[localhost:%d]: SERVER shutting down ... " %(self.port))
            self.peer.shutdown()
