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

    def __init__(self, peerID, port):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port
        self.peerID = peerID
        self.socket.bind("tcp://*:%d" %(self.port))
        threading.Thread.__init__(self)


    def run(self):
        while True:
            zipcode = self.port
            temperature = randrange(-80, 135)
            relhumidity = randrange(10, 60)
            updateString = str(zipcode) + " " + str(temperature) + " " + str(relhumidity)
            self.socket.send_string(updateString)
            print("[SERVER %d]: sent update %s"  %(self.peerID, updateString))
            time.sleep(0.5)  # set to 0.5



'''if __name__ == '__main__':
    server = Server(5556)
    server.run()'''