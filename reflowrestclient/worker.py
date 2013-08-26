import abc
import json
import logging
import sys
import time

from reflowrestclient.daemon import Daemon
import reflowrestclient.utils as rest


WORKER_CONF = '/etc/reflow_worker.conf'


class Worker(Daemon):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, name):
        # a Worker can have only one host
        self.host = host
        self.name = name
        self.assigned_pr_id = None

        # the token is the Worker's identifier to the host (i.e. password)
        # but it is not stored in the source code
        # All worker tokens on a system are stored in /etc/reflow-worker.conf
        try:
            worker_json = json.load(open(WORKER_CONF, 'r'))
            self.token = worker_json[host][name]
            del(worker_json)
        except Exception as e:
            message = "No token found for worker. Check the config file %s\n"
            sys.stderr.write(message % WORKER_CONF)
            sys.stderr.write(e.message)
            sys.exit(1)

        # verify worker with the host
        try:
            result = rest.verify_worker(self.host, self.token)
            self.genuine = result['data']['worker']  # should be True
            if self.genuine is not True:
                raise Exception
        except Exception as e:
            message = "Could not verify worker %s with host %s\n"
            sys.stderr.write(message % (self.name, self.host))
            sys.stderr.write(e.message)
            sys.exit(1)

        # TODO: define and verify a location to save stuff
        # for now put the PID file in /tmp
        pid_file = '/tmp/reflow-worker-%s.pid' % self.name

        super(Worker, self).__init__(pid_file)

    def run(self):
        logging.basicConfig(
            filename='/Users/swhite/Desktop/worker.log',
            filemode='w',
            level=logging.DEBUG)

        while True:
            self.loop()
            time.sleep(1)

    def loop(self):
        # Once inside the loop, try VERY hard not to exit,
        # just capture and log all Exceptions and Errors
        if self.assigned_pr_id is None:
            try:
                viable_requests = rest.get_viable_process_requests(self.host, self.token)
            except Exception as e:
                logging.warning("Exception: ", e.message)
            print viable_requests
