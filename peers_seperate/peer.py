#
#   Peer: consisting of 1 server & n clients
#   calls server + clients as threads
#   shuts clients down, when server wants to end the connection
#

from client import Client
from server import Server
from logging.logger import Logger
import os
import argparse

class Peer:

    def __init__(self, hostport, others, coordinates, tracefile, logDir):
        # 1 publisher
        # n subscribers
        self.logger = Logger(logDir);
        self.clients = []
        self.server = Server(hostport, coordinates, tracefile, self)
        self.addresses = others.split(',')
        for i in range(len(self.addresses)):
            self.clients.append(Client(hostport, self.addresses[i].strip(), self))

        self.server.start()
        for i in range(len(self.clients)):
            self.clients[i].start()

        self.server.join()
        for client in self.clients:
            client.join()

    def shutdown(self):
        for client in self.clients:
            client.shutdown()
        self.logger.closeFile()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start a peer with one server and several clients.')

    parser.add_argument('--serverPort', type=int,
                        help='the port number of the server')

    parser.add_argument('--clients', type=str,
                        help='IP-address and port of the clients; \nExample: "localhost:5557,localhost:5558,localhost:5559"')

    parser.add_argument('--coordinates', type=str,
                        help='coordinates of the left upper corner and the right lower corner for the rectangle '
                             'which the server should observe; \nExample: "0,65000,65000,0"')

    parser.add_argument('--tracefile', type=str,
                        help='the path to the tracefile which the server should read from')

    parser.add_argument('--logDir', type=str,
                        help='the directory in which the logfile should be saved')

    args = parser.parse_args()

    # --serverPort=5556
    # --addresses="localhost:5557, localhost:5558, localhost:5559"
    #log the params in file

    if(not(os.path.exists(args.tracefile))):
        print("Path to tracefile does not exist!\n")
    else:
        paramsLog = open("paramsLog.txt", "w");
        paramsLog.write("--serverPort=%d\n--clients=%s\n--coordinates=%s\n--logDir=%s"
                    %(args.serverPort, args.clients, args.coordinates, args.logDir));
        paramsLog.close()
        Peer(args.serverPort, args.clients, args.coordinates, args.tracefile, args.logDir)

