#
#   Weather update server
#   Binds PUB socket to tcp://*:5556
#   Publishes random weather updates
#

import zmq
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
            line = logfile.readline().strip('\n').split('\t')[1]
            self.socket.send_string(line)
            print("[localhost:%d]: sent update %s" %(self.port, line))
            count += 1
            time.sleep(0.5)  # set to 0.5

        logfile.close()
        self.socket.send_string("EOF")
        if(self.peer != None):
            print("[localhost:%d]: SERVER shutting down ... " %(self.port))
            self.peer.shutdown()
            self.socket.close()
