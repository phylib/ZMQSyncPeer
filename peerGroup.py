

from peer import Peer
import argparse

class peerGroup:
    peers = []
    def __init__(self, n, addresses):
        # n peers --> n addresses
        # 1 peer = 1 server + (n-1) clients
        for i in range(n):
            others = addresses.split(', ')[:]
            hostport = int(others[i].split(':')[1])
            del others[i]
            self.peers.append(Peer(n-1, hostport, others))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start a peergroup  N peers.')
    parser.add_argument('--N', type=int,
                        help='the number of peers in the group')

    parser.add_argument('--addresses', type=str,
                        help='IP-address and port of the peers')

    args = parser.parse_args()

    if(args.N != len(args.addresses.split(', '))):
        raise ValueError('Number of peers must be the same as the number addresses!')

    #"localhost:5556, localhost:5557, localhost:5558, localhost:5559"
    myGroup = peerGroup(args.N, args.addresses)

    for peer in myGroup.peers:
       peer.start()


