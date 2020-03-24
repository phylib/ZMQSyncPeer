#
#   Server: sends messages to clients
#   Binds PUB socket to tcp://*:5556
#

import zmq
import threading
import time
import protoGen.chunkChanges_pb2
from rectangle import Rectangle

class Server (threading.Thread):

    def __init__(self, port, coordinates, peer=None):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.port = port
        self.peer = peer
        self.socket.bind("tcp://*:%d" %(self.port))
        self.versions = {}
        self.rectangle = Rectangle(int(coordinates.split(',')[0]), int(coordinates.split(',')[1]),
                                   int(coordinates.split(',')[2]), int(coordinates.split(',')[3]))
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

            #reset this list before the changes of the next line are observed
            del self.chunkChanges.chunks[:]

            #split the line in different coordinates and update them in the
            #versions-Dictionary
            self.checkSingleCoordinates(line)

            #if chunkChanges not empty
            if(len(self.chunkChanges.chunks)>0):
                string = self.chunkChanges.SerializeToString()
                self.printAllChunkChanges()
                #print("[localhost:%d]: sent update %s" % (self.port, string))
                self.socket.send(string)
                #log the chunkChange
                self.logChunkChanges(self.chunkChanges.chunks, time.time())

            count += 1
            time.sleep(0.5) # seconds

        logfile.close()

        #print final versions-Dictionary
        self.printVersions()
        self.createChunk(0, 0, 0, True)
        string = self.chunkChanges.SerializeToString()
        self.socket.send(string)

        if(self.peer != None):
            print("[localhost:%d]: SERVER shutting down ... " %(self.port))
            self.peer.shutdown()
            self.socket.close()

    def checkSingleCoordinates(self, line):
        for coordinate in line.split(';'):
            x = int(coordinate.split(',')[0])
            y = int(coordinate.split(',')[1])

            if (self.rectangle.inRectangle(x, y)):
                self.updateVersion(coordinate);

                # protobufmessage
                self.createChunk(x, y, self.versions[coordinate], False)

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

    def createChunk(self, x, y, data, eof):
        if(eof==True):
            del self.chunkChanges.chunks[:]
        else:
            self.chunk.x = x
            self.chunk.y = y
            self.chunk.data = data
        self.chunk.eof = eof
        self.chunkChanges.chunks.extend([self.chunk])

    def logChunkChanges(self, chunks, timestamp):
        if(self.peer!=None):
            for chunk in chunks:
                self.peer.logger.logChunkUpdateProduced(chunk, timestamp)