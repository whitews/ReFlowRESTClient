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
                get_viable_process_requests('localhost:8000', self.token)
                time.sleep(5)
                logging.info('sleeping\n')
            except Exception as e:
                logging.warning("Exception: ", e.message)


if __name__ == "__main__":
    token = 'some-secret'

    worker = MyWorker(token, '/tmp/example_worker.pid')

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