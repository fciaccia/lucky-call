import multiprocessing as mp
import sys

from time import sleep

from lucky_call.common import KEYWORD, PRIME, MAX_NUM


class RadioServer(mp.Process):

    def __init__(self, pub_queue, req_queue, db_queue):
        mp.Process.__init__(self)
        self.pub_queue = pub_queue
        print("server ",pub_queue)
        print("server ",pub_queue._queues)
        self.req_queue = req_queue
        self.db_queue = db_queue
        self._magic_number = 0
        self._num_callers = 0
        self._last_pid = 0

    # Setter methods in case of db recovery
    def set_last_pid(self, last_pid):
        self._last_pid = last_pid

    def set_num_callers(self, num_callers):
        self._num_callers = num_callers

    def set_magic_number(self, magic_number):
        self._magic_number = magic_number

    def check_winner(self):
        if self._magic_number % PRIME == 0:
            print("And our winner is %d! Congratulations!"%(self._last_pid))
            return True
        else:
            return False

    def run(self):
        print("Started RadioServer")
        sleep(5)
        # Publish keyword to RadioClients
        self.pub_queue.publish(KEYWORD)
        print("Published keyword ", KEYWORD)

        winner = False
        while True:
            try:
                req = self.req_queue.get()
                if req is None:
                    break
                print("Received message from caller ", req['pid'])
                num = int(req['message'].split(KEYWORD)[1])
                self._num_callers += 1

                if num > MAX_NUM:
                    print("Invalid number %d from caller %d"%(num, req['pid']))

                self._last_pid = req['pid']
                self._magic_number += num

                # Write to db
                db_queue.put(
                    {
                        'last_pid': self._last_pid,
                        'num_callers': self._num_callers,
                        'magic_number': self._magic_number
                    }
                )

                winner = self.check_winner()
                if winner:
                    break

            except Exception as e:
                print(e)
                sys.exit(0)

        db_queue.put(None)
        if not winner:
            print("Sorry but nobody won today! Better luck next time.")