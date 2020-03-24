#
#   Server: sends messages to clients
#   Binds PUB socket to tcp://*:5556
#

import zmq
import threading
import time
import gzip
import math
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
        # we don't need the very first line at index 0
        count = 0
        logfile = open("ChunkChanges-very-distributed.csv", "r")
        allLines = logfile.readlines()
        allLines.remove(allLines[0])
        logfile.close()

        # get maxX, minX, maxY, minY
        area = self.getMaximumsAndMinimums(allLines)
        print("\nAREA: maxX: %d, minX: %d, maxY: %d, minY: %d\n" %(area.rightLowerX, area.leftUpperX, area.leftUpperY, area.rightLowerY))

        while count < 20:
            line = allLines[count].strip('\n').split('\t')[1]

            #reset this list before the changes of the next line are observed
            del self.chunkChanges.chunks[:]

            #split the line in different coordinates and update them in the
            #versions-Dictionary
            self.checkSingleCoordinates(line)

            #if chunkChanges not empty
            if(len(self.chunkChanges.chunks)>0):
                string = self.chunkChanges.SerializeToString()
                string = gzip.compress(string, 1);
                self.printAllChunkChanges()
                #print("[localhost:%d]: sent update %s" % (self.port, string))
                self.socket.send(string)
                #log the chunkChange
                self.logChunkChanges(self.chunkChanges.chunks, time.time())

            count += 1
            time.sleep(0.5) # seconds

        #print final versions-Dictionary
        self.printVersions()
        self.createChunk(0, 0, 0, True)
        string = self.chunkChanges.SerializeToString()
        string = gzip.compress(string, 1)
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

    def getMaximumsAndMinimums(self, lines):
        maxX = -math.inf
        maxY = -math.inf
        minX = math.inf
        minY = math.inf

        for line in lines:
            line = line.strip('\n').split('\t')[1]
            for coordinates in line.split(";"):
                x = int(coordinates.split(',')[0])
                y = int(coordinates.split(',')[1])
                if(x > maxX):
                    maxX = x
                if(x < minX):
                    minX = x
                if(y > maxY):
                    maxY = y
                if(y < minY):
                    minY = y
        return Rectangle(minX, maxY, maxY, minY)