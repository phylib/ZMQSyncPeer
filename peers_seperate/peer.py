
from client import Client
from server import Server
import argparse

class Peer:

    def __init__(self, n, port, others):
        # 1 publisher
        # n subscribers
        self.clients = []
        self.server = Server(port, self)
        self.addresses = others.split(',')
        for i in range(len(self.addresses)):
            self.clients.append(Client(port, self.addresses[i].strip()))

        self.server.start()
        for i in range(len(self.clients)):
            self.clients[i].start()

        self.server.join()
        for i in range(len(self.clients)):
            self.clients[i].join()

    def shutdown(self):
        for client in self.clients:
            client.shutdown()

if __name__ == "__main__":
    #Peer(4, 5556, ["localhost:5557", "localhost:5558", "localhost:5559"])

    parser = argparse.ArgumentParser(description='Start a peer with one server and N clients.')
    parser.add_argument('--N', type=int,
                        help='the number of clients in a peer')

    parser.add_argument('--port', type=int,
                        help='the port number of the server')

    parser.add_argument('--others', type=str,
                        help='IP-address and port of the clients')

    args = parser.parse_args()

    if(args.N != len(args.others.split(','))):
        raise ValueError('Number of clients must be the same as the number of other addresses!')

    #"localhost:5557, localhost:5558, localhost:5559"
    Peer(args.N, args.port, args.others)
