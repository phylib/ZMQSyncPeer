import zmq
import threading
import time
import gzip
import math
import protoGen.chunkChanges_pb2
from rectangle import Rectangle
import logging

class Server (threading.Thread):
    """
       The Server class publishes updates to its clients.

       The server is assigned a certain area which it has to
       observe. If an update occurs in its area the server
       has to broadcast this update to its clients. The server
       is part of a peer and therefore realized as a thread.
    """

    def __init__(self, port, coordinates, tracefile, testing, peer=None):
        """
           Initializes the server.
           :param port: specifies the port number on which the server broadcasts its updates
           :type port: int
           :param coordinates: defines the rectangle to observe in the form x1,y1,x2,y2
           :type coordinates: str
           :param tracefile: the path to the tracefile which the server reads from
           :type tracefile: str
           :param testing: if true the server only reads 20 lines from the tracefile, else it reads everything
           :type testing: bool
           :param peer: defines the peer of which the server is part of
           :type peer: Peer (if defined), default is None
        """
        self.lock = threading.Lock()
        self.port = port
        self.logInfo("initializing")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.peer = peer
        self.tracefile = tracefile
        self.testing = testing
        self.socket.bind("tcp://*:%d" %(self.port))
        self.versions = {}
        self.rectangle = Rectangle(int(coordinates.split(',')[0]), int(coordinates.split(',')[1]),
                                   int(coordinates.split(',')[2]), int(coordinates.split(',')[3]))
        self.chunk = protoGen.chunkChanges_pb2.Chunk();
        self.chunkChanges = protoGen.chunkChanges_pb2.ChunkChanges();
        self.chunkChanges.hashKnown = False;
        threading.Thread.__init__(self)


    def run(self):
        """
           Starts the observing process of the servers assigned area.

           At first the server needs to read all lines out of
           "ChunkChanges-very-distributed.csv", which documents all the changes that happened.
           Because this file also contains negative coordinates a shift of
           all coordinates needs to be done. If the shifted coordinates are
           in the servers assigned area then the server publishes an update.
           The message format for the updates are defined in chunkChanges.proto.
           These messages are serialized to strings and compressed with gzip before they are sent.
           The observed changes are also logged in the logfile of the peer's logger-instance.
        """
        self.logInfo('running ...')
        count = 0
        tracefile = open(self.tracefile, "r")
        allLines = tracefile.readlines()
        allLines.remove(allLines[0])
        tracefile.close()
        self.logInfo('read tracefile -> %s' % (self.tracefile))
        # get maxX, minX, maxY, minY
        area = self.getMaximumsAndMinimums(allLines)
        print("\nAREA: maxX: %d, minX: %d, maxY: %d, minY: %d\n" %(area.maxX, area.minX, area.maxY, area.minY))

        shiftingDistances = self.getShiftingDistances(area)
        allLines.extend(["EOF"])
        line = allLines[count]

        self.logInfo('starting to publish updates ...')
        while line!="EOF":
            if (self.testing and count == 20):
                break
            line = line.strip('\n').split('\t')[1]

            #reset this list before the changes of the next line are observed
            del self.chunkChanges.chunks[:]

            #split the line in different coordinates and update them in the
            #versions-Dictionary
            self.checkSingleCoordinates(line, shiftingDistances[0], shiftingDistances[1])

            #if chunkChanges not empty
            if(len(self.chunkChanges.chunks)>0):
                string = self.chunkChanges.SerializeToString()
                string = gzip.compress(string, 1);
                self.printAllChunkChanges()
                #print("[localhost:%d]: sent update %s" % (self.port, string))
                self.logInfo('published update')
                self.socket.send(string)
                self.logChunkChanges(self.chunkChanges.chunks, time.time(), len(self.chunkChanges.chunks))

            count += 1
            time.sleep(0.5)

            line = allLines[count]

        # prepare for shutdown
        self.printVersions()
        self.createChunk(0, 0, 0, True)
        string = self.chunkChanges.SerializeToString()
        string = gzip.compress(string, 1)
        self.socket.send(string)
        self.logInfo('published end-message')

        if(self.peer != None):
            print("[localhost:%d]: SERVER shutting down ... " %(self.port))
            self.peer.shutdown()
            self.socket.close()
            self.logInfo('shut down')


    def checkSingleCoordinates(self, line, xShift, yShift):
        """
        Shift the coordinates so that all of them are
        non-negative. Then check if they are inside the
        rectangle the server has to observe. Keep track
        of the version of the relevant coordinates.
        :param line: contains the coordinates of all changes at a certain point in time
        :type line: str
        :param xShift: the shifting distance for the x-coordinate
        :type xShift: int
        :param yShift: the shifting distance for the y-coordinate
        :type yShift: int
        """
        for coordinate in line.split(';'):

            # shift x and y so that all coordinates are positive
            x = int(coordinate.split(',')[0]) + xShift
            y = int(coordinate.split(',')[1]) + yShift
            coordinate = str("%d,%d" %(x,y))

            if (self.rectangle.inRectangle(x, y)):
                self.updateVersion(coordinate);

                # send protobuf-message
                self.createChunk(x, y, self.versions[coordinate], False)

    def updateVersion(self, key):
        """
        If the changed coordinate is already
        in our version-dictionary, then update its version.
        Else add it to the dictionary with version 1.
        :param key: the coordinates of a certain change
        :type key: str
        """
        if(key in self.versions):
            self.versions[key]+=1;
        else:
            self.versions[key]=1;

    def printVersions(self):
        """
        Prints all coordinates and their final
        version after the server is finished with
        observing the changes inside its area.
        """
        print("\n### All coordinates and their final versions: ###")
        for x, y in self.versions.items():
            print(x + ": " + str(y));
        print("\n")

    def printAllChunkChanges(self):
        """
        Print the changes of all relevant coordinates
        which happened at a certain point of time.
        """
        string = ""
        for chunk in self.chunkChanges.chunks:
            string+= str(chunk.x) + "," + str(chunk.y) + ";"
        print("[localhost:%d]: sent update %s" % (self.port, string))

    def createChunk(self, x, y, data, eof):
        """
        Create a chunk with the given parameters
        and put the chunk in the list of chunkChanges.
        All chunks in this list represent changes that happened
        at the same point of time.
        :param x: the x coordinate
        :type x: int
        :param y: the y coordinate
        :type y: int
        :param data: the version of this chunk
        :type data: int
        :param eof: represents if this is the last message or not
        :type eof: bool
        """
        if(eof==True):
            del self.chunkChanges.chunks[:]

        self.chunk.x = x
        self.chunk.y = y
        self.chunk.data = data
        self.chunk.eof = eof
        self.chunkChanges.chunks.extend([self.chunk])

    def logChunkChanges(self, chunks, timestamp, numChanges):
        """
        Write the sent update in a logfile.
        :param chunks: the list of changed chunks
        :type chunks: list of Chunk-objects
        :param timestamp: the point of time at which the server sent the update
        :type timestamp: time
        :param numChanges: the number of changed relevant chunks per line of the tracefile
        :type: int
        """
        if(self.peer!=None):
            for chunk in chunks:
                self.peer.logger.logChunkUpdateProduced(chunk, timestamp, numChanges)

    def getMaximumsAndMinimums(self, lines):
        """
        Get the maximum and minimum coordinates
        of the area where all changes are happening.
        :param lines: all lines of the file where we read the changes from
        :type lines: list of strings
        :return: the rectangle representing the whole area
        """
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

    def getShiftingDistances(self, area):
        """
        Calculate the shifting distance for
        the coordinates.
        :param area: the whole area where changes are happening
        :type area: Rectangle
        :return: tuple of the shifting distance for x and the shifting distance for y
        """
        treeSize = 65536
        width = area.maxX - area.minX
        height = area.maxY - area.minY
        xCenter = area.minX + (width / 2)
        yCenter = area.minY + (height / 2)
        xShift = int((treeSize / 2) - xCenter)
        yShift = int((treeSize / 2) - yCenter)
        return (xShift, yShift)

    def logInfo(self, message):
        self.lock.acquire()
        logging.info('[SERVER@localhost:%d]: %s' %(self.port, message))
        self.lock.release()