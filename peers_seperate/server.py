#
#   Server: sends messages to clients
#   Binds PUB socket to tcp://*:5556
#

import zmq
import threading
import time
import protoGen.chunkChanges_pb2

class Server (threading.Thread):

    def __init__(self, port, peer=None):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port
        self.peer = peer
        self.socket.bind("tcp://*:%d" %(self.port))
        self.versions = {}
        self.chunk = protoGen.chunkChanges_pb2.Chunk();
        self.chunkChanges = protoGen.chunkChanges_pb2.ChunkChanges();
        self.chunkChanges.hashKnown = False;
        threading.Thread.__init__(self)


    def run(self):
        count = 0
        logfile = open("ChunkChanges-very-distributed.csv", "r")
         #read first line "away" --> no important data here!
        logfile.readline()

        while count < 20:
            line = logfile.readline().strip('\n').split('\t')[1]

            #split the line in different coordinates and update them in the
            #versions-Dictionary
            for coordinate in line.split(';'):
                self.updateVersion(coordinate);

                #protobufmessage
                self.chunk.x = int(coordinate.split(',')[0])
                self.chunk.y = int(coordinate.split(',')[1])
                self.chunk.data = self.versions[coordinate];
                self.chunk.eof = False;
                string = self.chunk.SerializeToString()

                # for printing the decoded string (chunk)
                print("[localhost:%d]: send update %d, %d" % (self.port, self.chunk.x, self.chunk.y))

                # for printing the encoded chunk (string)
                # print("[localhost:%d]: sent update %s" % (self.port, string))

                self.socket.send(string)

            count += 1
            time.sleep(0.5) # seconds

        logfile.close()

        #print final versions-Dictionary
        self.printVersions()

        self.chunk.eof = True;
        string = self.chunk.SerializeToString()
        self.socket.send(string)

        if(self.peer != None):
            print("[localhost:%d]: SERVER shutting down ... " %(self.port))
            self.peer.shutdown()
            self.socket.close()

    def updateVersion(self, key):
        if(key in self.versions):
            self.versions[key]+=1;
        else:
            self.versions[key]=1;

    def printVersions(self):
        print("\n### All coordinates and their final versions: ###")
        for x, y in self.versions.items():
            print(x + " : " + str(y));
        print("\n")