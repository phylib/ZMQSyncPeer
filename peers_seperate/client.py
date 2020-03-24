#
#  Client: reads messages from server
#  Connects SUB socket to tcp://localhost:5556
#

import zmq
import threading
import time
import gzip
import protoGen.chunkChanges_pb2

class Client (threading.Thread):
    def __init__(self, hostport, address, peer=None):
        #  Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.hostport = hostport
        self.address = address
        self.peer = peer
        self.chunkChanges = protoGen.chunkChanges_pb2.ChunkChanges();
        self.chunkChanges.hashKnown = False;
        threading.Thread.__init__(self)

    def run(self):
        print("[%s]: connecting to server …" %(self.address))
        self.socket.connect("tcp://localhost:%d" %(self.hostport) )
        # Subscribe to hostport
        self.zip_filter = ''

        # Python 2 - ascii bytes to unicode str
        if isinstance(self.zip_filter, bytes):
            self.zip_filter = self.zip_filter.decode('ascii')
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.zip_filter)

        while True:
            string = self.socket.recv()
            string = gzip.decompress(string)
            self.chunkChanges.ParseFromString(string);
            if(len(self.chunkChanges.chunks)==1 and self.chunkChanges.chunks[0].eof == True):
                break;

            self.logChunkChanges(self.chunkChanges.chunks, time.time())
            self.printAllChunkChanges()
            #print("[%s]: got update %s" % (self.address, string))


    def shutdown(self):
        print("[%s]: CLIENT shutting down ... "  % (self.address))
        self.socket.close()

    def printAllChunkChanges(self):
        string = ""
        for chunk in self.chunkChanges.chunks:
            string+= str(chunk.x) + "," + str(chunk.y) + ";"
        print("[%s]: got update %s" % (self.address, string))

    def logChunkChanges(self, chunks, timestamp):
        if(self.peer!=None):
            for chunk in chunks:
                self.peer.logger.logChunkUpdateReceived(chunk, timestamp)
