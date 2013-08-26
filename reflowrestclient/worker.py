import abc
from reflowrestclient.daemon import Daemon


class Worker(Daemon):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, token, pid_file):
        # a Worker can have only one host
        self.host = host

        # the token is the Worker's identifier to the host (i.e. password)
        self.token = token

        # TODO: check-in with host, else quit

        # TODO: define and verify a location to save stuff

        super(Worker, self).__init__(pid_file)

    @abc.abstractmethod
    def run(self):
        """
        Override
        """
        return
