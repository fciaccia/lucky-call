import multiprocessing as mp
import sys

from lucky_call.client.radio_client import RadioClient
from lucky_call.server.radio_server import RadioServer
from lucky_call.server.db_writer import DBWriter
from lucky_call.common import PublishQueue, Defaults


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
    pub_queue = PublishQueue()
    req_queue = mp.Queue()
    db_queue = mp.Queue()

    # Setup main radio server and db processes
    server = RadioServer(pub_queue, req_queue, db_queue)
    db_writer = DBWriter(args_dict['db_file'], db_queue)

    # Check if db already exists - i.e. recovering from failure
    try:
        with open(args_dict['db_file'], 'r') as f:
            line = f.readline().split()
            server.set_last_pid(int(line[0]))
            server.set_num_callers(int(line[1]))
            server.set_magic_number(int(line[2]))
            # Check if the simulation terminated just before we announced the winner
            if server.check_winner():
                sys.exit(0)
    except FileNotFoundError:
        # First run or graceful termination, nothing to recover
        pass

    # Setup clients and run the constest
    try:
        clients = []
        for _ in range(args_dict['num_clients']):
            client = RadioClient(pub_queue, req_queue)
            client.start()
            clients.append(client)

        server.start()
        db_writer.start()

        #for client in clients:
        #    client.join()

        server.join()

        # When server finishes terminate gracefully db writer process
        os.remove(args_dict['db_file'])

    except KeyboardInterrupt:
        # Terminate gracefully all clients, server, and db
        pub_queue.put(None)
        req_queue.put(None)
        db_queue.put(None)

if __name__ == "__main__":
    main()