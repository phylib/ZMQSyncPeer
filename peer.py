
from client import Client
from server import Server
import argparse
class Peer:
    clients = []
    def __init__(self, n, port, others):
        # 1 publisher
        # n subscribers
        self.server = Server(port)
        self.server.start()  # Start publisher thread
        for i in range(n):
            self.clients.append(Client(port, others[i], i))
            self.clients[i].start()  # Start subscriber threads




    def shutdown(self):

        self.server.shutdown()

if __name__ == '__main__':
    # Read cmd params
    parser = argparse.ArgumentParser(description='Start a peer with one server and N clients on the given port.')
    parser.add_argument('--N', type=int,
                        help='the number of clients in the peer')
    parser.add_argument('--port', type=int,
                        help='the port for the server which the clients should connect to')

    parser.add_argument('--others', type=str,
                        help='IP-address and port of the clients')

    args = parser.parse_args()

    if(args.N != len(args.others.split(', '))):
        raise ValueError('Number of clients must be the same as the number of other IP-addresses!')

    others = args.others.split(', ')
    Peer(args.N, args.port, others)


    # Start the client

    # Kill the client...