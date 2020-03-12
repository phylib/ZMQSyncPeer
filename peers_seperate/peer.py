
from client import Client
from server import Server
import argparse

class Peer:

    def __init__(self, hostport, others):
        # 1 publisher
        # n subscribers
        self.clients = []
        self.server = Server(hostport, self)
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
    #Peer(4, 5556, ["localhost:5557", "localhost:5558", "localhost:5559"])

    parser = argparse.ArgumentParser(description='Start a peer with one server and several clients.')

    parser.add_argument('--serverPort', type=int,
                        help='the port number of the server')

    parser.add_argument('--clients', type=str,
                        help='IP-address and port of the clients')

    args = parser.parse_args()

    #"localhost:5557, localhost:5558, localhost:5559"
    Peer(args.serverPort, args.clients)
