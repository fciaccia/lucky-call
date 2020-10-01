import multiprocessing as mp
import os
import sys

from random import randrange
from time import sleep

from lucky_call.common import KEYWORD, MAX_NUM

class RadioClient(mp.Process):

    def __init__(self, pub_queue, req_queue):
        mp.Process.__init__(self)
        print("client ",pub_queue)
        print("client ",pub_queue._queues)
        self.sub_queue = pub_queue.register()
        print("client ",pub_queue._queues)
        print("client ",self.sub_queue)
        self.req_queue = req_queue

    def run(self):
        print("Started RadioClient ", os.getpid())
        while True:
            try:
                word = self.sub_queue.get()
                print("Received word ", word)
                if word is None:
                    break
                if word == KEYWORD:
                    # Simulate random radio delay by waiting up to 1s
                    sleep(randrange(0,999)/1000)

                    # Generate request with random number
                    self.req_queue.put(
                        {
                            'pid': os.getpid(),
                            'message': KEYWORD+str(randrange(0,MAX_NUM))
                        }
                    )
                    # Terminate client after sending request
                    break
                else:
                    continue
            except Exception as e:
                print(e)
                sys.exit(0)
