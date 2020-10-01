import multiprocessing as mp
import os

from enum import Enum

PRIME = 11
KEYWORD = "lucky"
MAX_NUM = 999


class Defaults(Enum):
    DEFAULT_DB_FILENAME = 'local.db'
    DEFAULT_NUM_CLIENTS = 100