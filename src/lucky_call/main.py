import multiprocessing as mp
import os
import sys

from lucky_call.client.radio_client import RadioClient
from lucky_call.server.radio_server import RadioServer
from lucky_call.server.db_writer import DBWriter
from lucky_call.common import Defaults


def main():

    import argparse
    parser = argparse.ArgumentParser(
        description="Radio lucky caller simulation system",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-f", "--db-file", default=Defaults.DEFAULT_DB_FILENAME.value,
                        help="Local database filename")
    parser.add_argument("-c", "--num-clients", type=int, default=Defaults.DEFAULT_NUM_CLIENTS.value,
                        help="number of radio clients")

    args = parser.parse_args()
    args_dict = vars(args)

    # Setup queues for IPC
    manager = mp.Manager()
    req_queue = manager.Queue()
    db_queue = manager.Queue()
    pub_queues = []

    # Setup clients
    clients = []
    for _ in range(args_dict['num_clients']):
        sub_queue = manager.Queue()
        pub_queues.append(sub_queue)
        client = RadioClient(sub_queue, req_queue)
        clients.append(client)

    # Setup main radio server and db processes
    server = RadioServer(pub_queues, req_queue, db_queue)
    db_writer = DBWriter(args_dict['db_file'], db_queue)

    # Check if db already exists - i.e. recovering from failure
    try:
        with open(args_dict['db_file'], 'r') as f:
            print("Recovering Database")
            line = f.readline().split()
            server.set_last_pid(int(line[0]))
            server.set_num_callers(int(line[1]))
            server.set_magic_number(int(line[2]))
            # Check if the simulation terminated just before we announced the winner
            if server.check_winner():
                os.remove(args_dict['db_file'])
                sys.exit(0)
    except FileNotFoundError:
        # First run or graceful termination, nothing to recover
        pass

    # Run the constest
    try:
        for c in clients:
            c.start()

        server.start()
        db_writer.start()

        for c in clients:
            c.join()
        server.join()

        # When server finishes terminate gracefully db writer process
        db_queue.put(None)
        os.remove(args_dict['db_file'])

    except KeyboardInterrupt:
        # Terminate gracefully all clients, server, and db
        for queue in pub_queues:
            queue.put(None)
        req_queue.put(None)
        db_queue.put(None)
        for c in clients:
            c.join()
        server.join()
        db_writer.join()


if __name__ == "__main__":
    main()
