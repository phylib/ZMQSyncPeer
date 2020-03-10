
from client import Client
from server import Server
import argparse
class Peer:
    clients = []
    def __init__(self, n):
        # 1 publisher
        # n subscriber
        self.server = Server()
        self.server.run() # Start publisher thread
        #for i in range(n):
        #    self.clients.append(Client())
        #    self.clients[len(self.clients)-1].start()

        pass

    def shutdown(self):

        self.server.shutdown()

if __name__ == '__main__':
    print("Hello World")
    # Read cmd params

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('integers', metavar='N', type=int, nargs='+',
                        help='an integer for the accumulator')
    parser.add_argument('--sum', dest='accumulate', action='store_const',
                        const=sum, default=max,
                        help='sum the integers (default: find the max)')

    args = parser.parse_args()
    # Start the client

    # Kill the client...