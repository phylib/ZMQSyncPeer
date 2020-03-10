

#
#   Weather update client
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import zmq
import threading

class Client (threading.Thread):
    def __init__(self, hostport, address):
        #  Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.hostport = hostport
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        print("[%s]: Collecting updates from weather server…" %(self.address))
        self.socket.connect("tcp://localhost:%d" %(self.hostport) )
        # Subscribe to hostport
        self.zip_filter = str(self.hostport)

        # Python 2 - ascii bytes to unicode str
        if isinstance(self.zip_filter, bytes):
            self.zip_filter = self.zip_filter.decode('ascii')
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.zip_filter)

        # Process 5 updates
        total_temp = 0

        for update_nbr in range(5):
            string = self.socket.recv_string()
            print(("[%s]: Got update " + string) % (self.address))
            zipcode, temperature, relhumidity = string.split()
            total_temp += int(temperature)

        print("[%s]: Average temperature for zipcode '%s' was %dF " % (
            self.address, self.zip_filter, total_temp / (update_nbr + 1))
                )
