#
#   Server: sends messages to clients
#   Binds PUB socket to tcp://*:5556
#

import zmq
import threading
import time
import protoGen.chunkChanges_pb2

class Server (threading.Thread):

    def __init__(self, port, leftUpperCorner, rightLowerCorner, peer=None):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port
        self.peer = peer
        self.socket.bind("tcp://*:%d" %(self.port))
        self.versions = {}
        self.chunk = protoGen.chunkChanges_pb2.Chunk();
        self.chunk.x = 0
        self.chunk.y = 0
        self.chunk.data = 0
        self.chunkChanges = protoGen.chunkChanges_pb2.ChunkChanges();
        self.chunkChanges.hashKnown = False;
        self.leftUpperX = int(leftUpperCorner.split(',')[0])
        self.leftUpperY = int(leftUpperCorner.split(',')[1])
        self.rightLowerX = int(rightLowerCorner.split(',')[0])
        self.rightLowerY = int(rightLowerCorner.split(',')[1])
        threading.Thread.__init__(self)


    def run(self):
        count = 0
        logfile = open("ChunkChanges-very-distributed.csv", "r")
         #read first line "away" --> no important data here!
        logfile.readline()

        while count < 20:
            line = logfile.readline().strip('\n').split('\t')[1]

            #reset this list before the changes of the next line are observed
            del self.chunkChanges.chunks[:]

            #split the line in different coordinates and update them in the
            #versions-Dictionary
            for coordinate in line.split(';'):
                x = int(coordinate.split(',')[0])
                y = int(coordinate.split(',')[1])

                if(x >= self.leftUpperX and x <= self.rightLowerX
                and y <= self.leftUpperY and y>= self.rightLowerY):
                    self.updateVersion(coordinate);

                    #protobufmessage
                    self.chunk.x = x
                    self.chunk.y = y
                    self.chunk.data = self.versions[coordinate];
                    self.chunk.eof = False;
                    self.chunkChanges.chunks.extend([self.chunk])

            #if chunkChanges not empty
            if(len(self.chunkChanges.chunks)>0):
                string = self.chunkChanges.SerializeToString()
                self.printAllChunkChanges()
                self.socket.send(string)

            count += 1
            time.sleep(0.5) # seconds

        logfile.close()

        #print final versions-Dictionary
        self.printVersions()

        self.chunk.eof = True;
        del self.chunkChanges.chunks[:]
        self.chunkChanges.chunks.extend([self.chunk])
        string = self.chunkChanges.SerializeToString()
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
            print(x + ": " + str(y));
        print("\n")

    def printAllChunkChanges(self):
        string = ""
        for chunk in self.chunkChanges.chunks:
            string+= str(chunk.x) + "," + str(chunk.y) + ";"
        print("[localhost:%d]: sent update %s" % (self.port, string))
