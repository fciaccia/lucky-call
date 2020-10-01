import multiprocessing as mp
import sys


class DBWriter(mp.Process):

    def __init__(self, filename, db_queue):
        mp.Process.__init__(self)
        self.filename = filename
        self.db_queue = db_queue

    def run(self):
        while True:
            try:
                req = self.db_queue.get()
                if req is None:
                    break
                with open(self.filename, 'w+') as db:
                    db.write(
                        str(req['last_pid'])+" " +
                        str(req['num_callers'])+" " +
                        str(req['magic_number']))
            except FileNotFoundError:
                print("Error writing to file "+self.filename)
                sys.exit(0)
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                print(e)
                sys.exit(0)
