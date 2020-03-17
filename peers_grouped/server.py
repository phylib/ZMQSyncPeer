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

    def __init__(self,port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port
        self.socket.bind("tcp://*:%d" %(self.port))
        threading.Thread.__init__(self)


    def run(self):
        while True:
            zipcode = self.port
            temperature = randrange(-80, 135)
            relhumidity = randrange(10, 60)
            updateString = str(zipcode) + " " + str(temperature) + " " + str(relhumidity)
            self.socket.send_string(updateString)
            print("[localhost:%d]: sent update %s" %(self.port, updateString))
            time.sleep(0.5)  # set to 0.5
