#
#   Peer: consisting of 1 server & n clients
#   calls server + clients as threads
#   shuts clients down, when server wants to end the connection
#

from client import Client
from server import Server
import argparse

class Peer:

    def __init__(self, hostport, others, leftUpperCorner, rightLowerCorner):
        # 1 publisher
        # n subscribers
        self.clients = []
        self.server = Server(hostport, leftUpperCorner, rightLowerCorner, self)
        self.addresses = others.split(', ')
        for i in range(len(self.addresses)):
            self.clients.append(Client(hostport, self.addresses[i]))

        self.server.start()
        for i in range(len(self.clients)):
            self.clients[i].start()

        self.server.join()
        for client in self.clients:
            client.join()

    def shutdown(self):
        for client in self.clients:
            client.shutdown()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start a peer with one server and several clients.')

    parser.add_argument('--serverPort', type=int,
                        help='the port number of the server')

    parser.add_argument('--clients', type=str,
                        help='IP-address and port of the clients')

    parser.add_argument('--leftUpperCorner', type=str,
                        help='the left upper corner coordinates for the rectangle which the server should observe')

    parser.add_argument('--rightLowerCorner', type=str,
                        help='the right lower corner coordinates for the rectangle which the server should observe')

    args = parser.parse_args()

    # --serverPort=5556
    # --addresses="localhost:5557, localhost:5558, localhost:5559"
    Peer(args.serverPort, args.clients, args.leftUpperCorner, args.rightLowerCorner)

