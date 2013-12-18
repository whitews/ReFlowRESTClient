import sys
from reflowrestclient.processing import worker


class MyWorker(worker.Worker):
    def validate_inputs(self):
        return True

    def process(self):
        return


if __name__ == "__main__":
    host = 'localhost:8000'
    name = 'good_worker'

    worker = MyWorker(host, name)
    worker.sleep = 5

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            worker.start(debug=True)
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