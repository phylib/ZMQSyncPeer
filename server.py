#
#   Weather update server
#   Binds PUB socket to tcp://*:5556
#   Publishes random weather updates
#

import zmq
from random import randrange

class Server:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://*:5556")

    def start(self):
        while True:
            zipcode = randrange(1, 100000)
            temperature = randrange(-80, 135)
            relhumidity = randrange(10, 60)
            self.socket.send_string("%i %i %i" % (zipcode, temperature, relhumidity))
