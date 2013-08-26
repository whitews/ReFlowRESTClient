import abc
import json
import sys
from reflowrestclient.daemon import Daemon

WORKER_CONF = '/etc/reflow_worker.conf'

class Worker(Daemon):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, name):
        # a Worker can have only one host
        self.host = host
        self.name = name

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

        # TODO: check-in with host, else quit

        # TODO: define and verify a location to save stuff
        pid_file = '/tmp/reflow-worker-%s.pid' % self.name

        super(Worker, self).__init__(pid_file)

    @abc.abstractmethod
    def run(self):
        """
        Override
        """
        return
