

#
#   Weather update client
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import sys
import argparse
import zmq
import threading

class Client (threading.Thread):
    def __init__(self, port, clientID=0):
        #  Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.id = clientID
        self.port = port
        threading.Thread.__init__(self)

    def run(self):
        print("[CLIENT %d]: Collecting updates from weather server…" %self.id)
        self.socket.connect("tcp://localhost:%d" %(self.port) )
        # Subscribe to zipcode, default is NYC, 10001
        self.zip_filter = str(self.port)

        # Python 2 - ascii bytes to unicode str
        if isinstance(self.zip_filter, bytes):
            self.zip_filter = self.zip_filter.decode('ascii')
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.zip_filter)

        # Process 5 updates
        total_temp = 0

        for update_nbr in range(5):
            string = self.socket.recv_string()
            print(("[CLIENT %d]: Got update " + string) % self.id)
            zipcode, temperature, relhumidity = string.split()
            total_temp += int(temperature)

        print("[CLIENT %d]: Average temperature for zipcode '%s' was %dF " % (
            self.id, self.zip_filter, total_temp / (update_nbr + 1))
                )

if __name__ == '__main__':
    # Create new threads

    threads = []
    numclients = 4

    for i in range(numclients):
        thread = Client(5556, i)
        threads.append(thread)

    # Start new Threads
    for i in range(numclients):
        threads[i].start()

    # Join Threads
    for i in range(numclients):
        threads[i].join()

    print("Exiting Main Thread")