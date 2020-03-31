import zmq
import threading
import time
import gzip
import protoGen.chunkChanges_pb2
import logging

class Client (threading.Thread):
    """
    The client class subscribes to a server
    and reads its published updates.
    """
    def __init__(self, serverAddress, address, peer=None):
        """
           Initializes the client.
           :param serverAddress: specifies the IP-address and port number on which the server broadcasts its updates
           :type serverAddress: str
           :param address: the IP-address and the port number of the client in the form IP-address:port number
           :type address: str
           :param peer: defines the peer of which the client is part of
           :type peer: Peer (if defined), default is None
        """
        self.address = address
        self.logInfo('initializing')
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.serverAddress = serverAddress
        self.peer = peer
        self.chunkChanges = protoGen.chunkChanges_pb2.ChunkChanges();
        self.chunkChanges.hashKnown = False
        threading.Thread.__init__(self)

    def run(self):
        """
        Starts the reading process of the server's updates.

        At first the client has to connect to the
        server through a TCP-Socket. Because we want to subscribe to
        all updates of the server we set the zip-filter to
        the empty string. After that the client can read the
        server's published updates. Before they can be
        transformed in the message format in chunkChanges.proto
        the client has to parse the decompressed string.
        Then the received update is logged in the logfile of the
        peer's logger instance. The reading process is
        stopped if the server sends the last message.
        """
        logging.debug("[%s]: connecting to server …" %(self.address))
        self.socket.connect("tcp://%s" %(self.serverAddress) )
        self.zip_filter = ''
        if isinstance(self.zip_filter, bytes):
            self.zip_filter = self.zip_filter.decode('ascii')
        # Subscribe to server
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.zip_filter)
        self.logInfo('subscribed to %s' % (self.serverAddress))

        while True:
            string = self.socket.recv()
            string = gzip.decompress(string)
            self.chunkChanges.ParseFromString(string);
            if(len(self.chunkChanges.chunks)==1 and self.chunkChanges.chunks[0].eof == True):
                self.logInfo('received end-message from %s' % (self.serverAddress))
                break;
            self.logInfo('received update from %s' % (self.serverAddress))
            self.logChunkChanges(self.chunkChanges.chunks, time.time())
            self.printAllChunkChanges()
            self.logInfo('processed update from %s' % (self.serverAddress))
            #print("[%s]: got update %s" % (self.address, string))


    def shutdown(self):
        """
        When the peer is shutting the client down
        the corresponding socket is closed.
        """
        logging.debug("[%s]: CLIENT shutting down ... "  % (self.address))
        self.socket.close()
        self.logInfo('shut down')

    def printAllChunkChanges(self):
        """
        Print the changed coordinates of the received update.
        """
        string = ""
        for chunk in self.chunkChanges.chunks:
            string+= str(chunk.x) + "," + str(chunk.y) + ";"
        logging.debug("[%s]: got update %s" % (self.address, string))

    def logChunkChanges(self, chunks, timestamp):
        """
        Write the received update in a logfile.
        :param chunks: the list of coordinates in the received update
        :type chunks: list of Chunk-Objects
        :param timestamp: the point of time at which we received this update
        :type timestamp: time
        """
        if(self.peer!=None):
            for chunk in chunks:
                self.peer.logger.logChunkUpdateReceived(chunk, timestamp)

    def logInfo(self, message):
        logging.info('[CLIENT@%s]: %s' % (self.address, message))
