from client import Client
from server import Server
from log.logger import Logger
import os
import sys
import argparse
import logging


class Peer:
    """
    The Peer class starts a server-thread and n client-threads
    where each client is subscribed to the server.

    Each peer consists of one server, one logger and n clients. The server
    as well as the clients are implemented as threads and started in the peer.
    All clients are subscribed to the server.
    When the peer is started via commandline several arguments are
    passed to it. These arguments are then passed to the server, the logger and
    the clients.

    """

    def __init__(self, server, others, coordinates, tracefile, logDir, testing):
        """
           Initializes the peer.
           :param hostport: specifies the port number on which the server broadcasts its updates
           :type hostport: int
           :param others: the IP-addresses and the port number of the clients in the form IP-address:port number
           :type others: str
           :param coordinates: defines the rectangle to observe in the form x1,y1,x2,y2
           :type coordinates: str
           :param tracefile: the path to the tracefile which the server reads from
           :type tracefile: str
           :param logDir: the path to the directory where the logfile should be saved
           :type logDir: str
           :param testing: if true the server only reads 20 lines from the tracefile, else it reads everything
           :type testing: bool
        """
        self.logger = Logger(logDir);
        self.clients = []
        self.server = Server(int(server.split(':')[1]), coordinates, tracefile, testing, self)
        self.addresses = others.split(',')

        for i in range(len(self.addresses)):
            self.clients.append(Client(server, self.addresses[i].strip(), self))

        self.server.start()
        for i in range(len(self.clients)):
            self.clients[i].start()

        self.server.join()
        for client in self.clients:
            client.join()

    def shutdown(self):
        """
        This method is called when the server shuts down.
        The peer then shuts all clients down and tells
        the logger to close the logfile.
        """
        for client in self.clients:
            client.shutdown()
        self.logger.closeFile()


def configure_loggers(logFolder, console=False):

    # Define log format
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Configure Default-Logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if console:
        # Configure logging to stdout
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        streamHandler.setLevel(logging.DEBUG)
        logger.addHandler(streamHandler)

    # Configure logging to File
    fileHandler = logging.FileHandler(logFolder + '/app.log')
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.INFO)
    logger.addHandler(fileHandler)



if __name__ == "__main__":
    """
    This method is called when the peer is 
    started via the commandline.
    Here the necessary arguments are parsed 
    and passed to the peer.
    """

    parser = argparse.ArgumentParser(description='Start a peer with one server and several clients.')

    parser.add_argument('--server', type=str, required=True,
                        help='the IP-address and port number of the server; \nExample:"localhost:5556"')

    parser.add_argument('--clients', type=str, required=True,
                        help='IP-address and port of the clients; \nExample: "localhost:5557,localhost:5558,localhost:5559"')

    parser.add_argument('--coordinates', type=str, required=True,
                        help='coordinates of the left upper corner and the right lower corner for the rectangle '
                             'which the server should observe; \nExample: "0,65000,65000,0"')

    parser.add_argument('--tracefile', type=str, required=True,
                        help='the path to the tracefile which the server should read from')

    parser.add_argument('--logDir', type=str, default="./log/",
                        help='the directory in which the logfile should be saved [Default: ./log/]')

    parser.add_argument('--testing', action='store_true',
                        help="if this argument is specified the server will only read 20 lines of its tracefile, else it will read the whole file")

    args = parser.parse_args()

    configure_loggers(args.logDir, console=args.testing)
    logging.info("Entering main...")

    if (not (os.path.exists(args.tracefile))):
        logging.fatal("Path to tracefile does not exist!")
        sys.exit()
    else:
        # log the params in file
        paramsLog = open("paramsLog.txt", "w");
        paramsLog.write("--server=%s\n--clients=%s\n--coordinates=%s\n--logDir=%s"
                        % (args.server, args.clients, args.coordinates, args.logDir));
        paramsLog.close()
        logging.info('Logged cmd arguments')
        Peer(args.server, args.clients, args.coordinates, args.tracefile, args.logDir, args.testing)
        logging.info("Exiting main...")
