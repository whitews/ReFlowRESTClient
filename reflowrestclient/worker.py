import abc
from reflowrestclient.daemon import Daemon


class Worker(Daemon):
    __metaclass__ = abc.ABCMeta

    def __init__(self, token, pid_file):
        self.token = token
        super(Worker, self).__init__(pid_file)

    @abc.abstractmethod
    def run(self):
        """
        Override
        """
        return
