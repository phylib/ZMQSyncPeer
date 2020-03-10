
from client import Client
from server import Server
import argparse
import threading

class Peer (threading.Thread):

    def __init__(self, id, n, port, others):
        '''   # 1 publisher
        # n subscribers
        self.server = Server(port)
        self.server.start()  # Start publisher thread
        for i in range(n):
            self.clients.append(Client(port, others[i], i))
            self.clients[i].start()  # Start subscriber threads '''
        self.id = id
        self.clients = []
        self.server = Server(self.id, port)
        for i in range(n):
            self.clients.append(Client(self.id, port, others[i], i))
        threading.Thread.__init__(self)

    def run(self):
        self.server.start()
        for i in range(len(self.clients)):
            self.clients[i].start()

    #def shutdown(self):
        #self.server.shutdown()

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