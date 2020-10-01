import multiprocessing as mp
import os
import sys

from random import randrange
from time import sleep

from lucky_call.common import KEYWORD, MAX_NUM


class RadioClient(mp.Process):

    def __init__(self, sub_queue, req_queue):
        mp.Process.__init__(self)
        self.sub_queue = sub_queue
        self.req_queue = req_queue

    def run(self):
        print("Started RadioClient ", os.getpid())
        while True:
            try:
                word = self.sub_queue.get()
                print("Client %d received word %s" % (os.getpid(), word))
                if word is None:
                    break
                if word == KEYWORD:
                    # Simulate random radio delay by waiting up to 1s
                    random_delay = randrange(0, 999)/1000
                    print("Client %d sleeping random delay %.3f" %
                          (os.getpid(), random_delay))
                    sleep(random_delay)

                    # Generate request with random number
                    self.req_queue.put(
                        {
                            'pid': os.getpid(),
                            'message': KEYWORD+str(randrange(100, MAX_NUM))
                        }
                    )
                    # Terminate client after sending request
                    break
                else:
                    continue
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                print(e)
                sys.exit(0)
