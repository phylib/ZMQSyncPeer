# ZMQ Client for Game State Synchronization

The basic concept of the client is that every game server publishes changes in 
it's region and subscribes to changes of all other servers. Therefore, ZMQ in
pub-sub mode is used. The server publishes it's changes under a specific port
and subscribes to all servers given as start parameters.

## Installation

To install all dependencies, use the Python3 Packet manager:

        pip3 install -r requirements.txt

## Execution

The main class for execution can be found in `peers_seperate/peer.py`. Please
execute `python3 peers_seperate/peer.py -h` to display information about 
executing the client.