
from client import Client
from server import Server
from peer import Peer
import argparse
class peerGroup:
    peers = []
    def __init__(self, n, addresses):
        # n peers --> n addresses
        # 1 peer = 1 server + (n-1) clients
        for i in range(n):
            others = addresses[:]
            hostport = int(others[i].split(':')[1])
            del others[i]
            print("Others: " + str(others))
            self.peers.append(Peer(n-1, hostport, others ))

if __name__ == '__main__':
    myGroup = peerGroup(4, ["localhost:5556", "localhost:5557", "localhost:5558", "localhost:5559"])
    for i in range(len(myGroup.peers)):
        print("[PEER %d]: " %i)
        print("\tServer: %d" %myGroup.peers[i].server.port)
        for client in myGroup.peers[i].clients:
            print("\tClient %d: %s" %(client.id, client.address))


