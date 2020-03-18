#
#  Client: reads messages from server
#  Connects SUB socket to tcp://localhost:5556
#

import zmq
import threading
import protoGen.chunkChanges_pb2

class Client (threading.Thread):
    def __init__(self, hostport, address):
        #  Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.hostport = hostport
        self.address = address
        self.chunk = protoGen.chunkChanges_pb2.Chunk();
        self.chunkChanges = protoGen.chunkChanges_pb2.ChunkChanges();
        self.chunkChanges.hashKnown = False;
        threading.Thread.__init__(self)

    def run(self):
        print("[%s]: collecting updates from weather server…" %(self.address))
        self.socket.connect("tcp://localhost:%d" %(self.hostport) )
        # Subscribe to hostport
        self.zip_filter = ''

        # Python 2 - ascii bytes to unicode str
        if isinstance(self.zip_filter, bytes):
            self.zip_filter = self.zip_filter.decode('ascii')
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.zip_filter)

        while True:
            string = self.socket.recv()
            self.chunk.ParseFromString(string)
            if(self.chunk.eof):
                break

            # for printing the decoded string (chunk)
            print("[%s]: got update %d, %d" % (self.address, self.chunk.x, self.chunk.y))

            # for printing the encoded chunk (string)
            # print("[%s]: got update %s" % (self.address, string))


    def shutdown(self):
        print("[%s]: CLIENT shutting down ... "  % (self.address))
        self.socket.close()
