
from client import Client
from server import Server
import threading

class Peer (threading.Thread):

    def __init__(self, n, port, others):
        # 1 publisher
        # n subscribers
        self.clients = []
        self.server = Server(port)
        for i in range(n):
            self.clients.append(Client(port, others[i]))
        threading.Thread.__init__(self)

    def run(self):
        self.server.start()
        for i in range(len(self.clients)):
            self.clients[i].start()
