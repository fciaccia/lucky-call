import multiprocessing as mp
import os

from enum import Enum

PRIME = 11
KEYWORD = "lucky"
MAX_NUM = 999


class Defaults(Enum):
    DEFAULT_DB_FILENAME = 'local.db'
    DEFAULT_NUM_CLIENTS = 100


class PublishQueue(object):
    ''' From https://stackoverflow.com/questions/31267366/how-can-i-implement-a-pub-sub-pattern-using-multiprocessing '''
    def __init__(self):
        self._queues = []
        self._creator_pid = os.getpid()

    def __getstate__(self):
        self_dict = self.__dict__
        self_dict['_queues'] = []
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)

    def register(self):
        q = mp.Queue()
        print("publish queue register", q)
        self._queues.append(q)
        return q

    def publish(self, val):
        print("publish queue publish", self._queues)
        for q in self._queues:
            print("Publishing message in queue ", q)
            q.put(val)

