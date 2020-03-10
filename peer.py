
from client import Client
from server import Server
import argparse
class Peer:
    clients = []
    def __init__(self, port, n):
        # 1 publisher
        # n subscriber
        self.server = Server(port)
        self.server.start()  # Start publisher thread
        for  i in range(n):
            self.clients.append(Client(port, i))
            self.clients[i].start()




    def shutdown(self):

        self.server.shutdown()

if __name__ == '__main__':
    #Peer(5556, 4)
    # Read cmd params
    parser = argparse.ArgumentParser(description='Start a peer with one server and N clients on the given port.')
    parser.add_argument('--N', type=int,
                        help='the number of clients in the peer')
    parser.add_argument('--port', type=int,
                        help='the port for the server which the clients should connect to')

    args = parser.parse_args()

    Peer(args.port, args.N)

    # Start the client

    # Kill the client...