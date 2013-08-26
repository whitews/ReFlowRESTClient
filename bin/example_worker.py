import os
import sys
import time
import logging
from reflowrestclient.worker import Worker
from reflowrestclient.utils import get_viable_process_requests


class MyWorker(Worker):
    def run(self):
        logging.basicConfig(
            filename='/Users/swhite/Desktop/worker.log',
            filemode='w',
            level=logging.DEBUG)

        while True:
            try:
                get_viable_process_requests(self.host, self.token)
                time.sleep(1)
                logging.info('sleeping\n')
            except Exception as e:
                logging.warning("Exception: ", e.message)


if __name__ == "__main__":
    host = 'localhost:8000'
    name = 'good_worker'

    worker = MyWorker(host, name)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            worker.start()
        elif 'stop' == sys.argv[1]:
            worker.stop()
        elif 'restart' == sys.argv[1]:
            worker.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)