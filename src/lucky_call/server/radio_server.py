import multiprocessing as mp
import queue
import sys

from time import sleep

from lucky_call.common import KEYWORD, PRIME, MAX_NUM


class RadioServer(mp.Process):

    def __init__(self, pub_queues, req_queue, db_queue):
        mp.Process.__init__(self)
        self.pub_queues = pub_queues
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
            print(
                "And our winner is %d with magic number %d! Congratulations!" %
                (self._last_pid, self._magic_number)
            )
            return True
        else:
            return False

    def run(self):
        print("Started RadioServer")

        # Publish keyword to RadioClients
        for pub_queue in self.pub_queues:
            pub_queue.put(KEYWORD)

        winner = False
        while True:
            try:
                req = self.req_queue.get(timeout=10)
                if req is None:
                    break
                num = int(req['message'].split(KEYWORD)[1])
                print("Received message from caller %d with number %d" %
                      (req['pid'], num))
                self._num_callers += 1

                if num > MAX_NUM:
                    print("Invalid number %d from caller %d" %
                          (num, req['pid']))

                self._last_pid = req['pid']
                self._magic_number += num

                # Write to db
                self.db_queue.put(
                    {
                        'last_pid': self._last_pid,
                        'num_callers': self._num_callers,
                        'magic_number': self._magic_number
                    }
                )

                winner = self.check_winner()
                if winner:
                    break

            except mp.TimeoutError:
                pass
            except queue.Empty:
                '''
                Was expecting to catch mp.TimeoutError when queue timed-out
                instead mp.get() is raising a queue.Empty; catching that for
                contest graceful termination
                '''
                break
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                print(e)
                sys.exit(0)

        self.db_queue.put(None)
        if not winner:
            print("Sorry but nobody won today! Better luck next time.")
