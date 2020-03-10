
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
    Peer(5556, 4)
    # Read cmd params
    '''parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()'''
    # Start the client

    # Kill the client...