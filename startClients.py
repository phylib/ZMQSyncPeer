import client
import threading
import time

exitFlag = 0

class clientThread (threading.Thread):
   def __init__(self, clientID):
      threading.Thread.__init__(self)
      self.clientID = clientID
      self.weatherClient = client.Client(clientID)

   def run(self):
      self.weatherClient.startObserving()


if __name__ == '__main__':
    # Create new threads
    threads = []

    for i in range(10):
        thread = clientThread(i+1)
        threads.append(thread)

    # Start new Threads
    for i in range(10):
        threads[i].start()

    # Join Threads
    for i in range(10):
        threads[i].join()

    print("Exiting Main Thread")


# Define a function for the thread
'''def start_client(clientID):
    weatherClient = client.Client(clientID)
    weatherClient.startObserving()

if __name__ == '__main__':
    try:
        # Create ten threads as follows
        for i in range(10):
            _thread.start_new_thread( start_client, (i+1, ) )
    except:
        print ("Error: unable to start thread")
    while 1:
        pass'''

