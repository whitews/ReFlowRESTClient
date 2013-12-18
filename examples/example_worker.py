import sys
from reflowrestclient.processing import worker


class MyWorker(worker.Worker):
    def validate_inputs(self):
        return True

    def process(self):
        print "Do some processing"
        return True

    def report_errors(self):
        return

    def upload_results(self):
        return


if __name__ == "__main__":
    host = 'localhost:8000'
    name = 'good_worker'

    usage = "usage: %s start|stop|restart" % sys.argv[0]

    worker = MyWorker(host, name, sleep=5)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            worker.start(debug=True)
        elif 'stop' == sys.argv[1]:
            worker.stop()
        elif 'restart' == sys.argv[1]:
            worker.restart()
        else:
            print "Unknown command"
            print usage
            sys.exit(2)
        sys.exit(0)
    else:
        print usage
        sys.exit(2)