import json
import logging
import sys
import time

import abc

from reflowrestclient.worker.daemon import Daemon
import reflowrestclient.utils as rest


WORKER_CONF = '/etc/reflow_worker.conf'


class Worker(Daemon):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, name):
        # a Worker can have only one host
        self.host = host
        self.name = name
        self.__assigned_pr = None

        # default sleep time between checking the server (in seconds)
        self.sleep = 300

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

    def get_process_inputs(self):
        input_dict = {}

        if self.__assigned_pr:
            if self.__assigned_pr.has_key('input_values'):
                for input in self.__assigned_pr['input_values']:
                    key = input['process_input']['input_name']

                    # TODO: handle default values if present and check for duplicates
                    input_dict[key] = input['value']
        return input_dict

    def run(self):
        logging.basicConfig(
            filename='/Users/swhite/Desktop/worker.log',
            filemode='w',
            level=logging.DEBUG)

        while True:
            self.loop()

    def loop(self):
        # Once inside the loop, try VERY hard not to exit,
        # just capture and log all Exceptions and Errors
        if self.__assigned_pr is None:
            try:
                viable_requests = rest.get_viable_process_requests(self.host, self.token)
            except Exception as e:
                logging.warning("Exception: ", e.message)

            if not viable_requests.has_key('data'):
                logging.warning("Error: Malformed response from ReFlow server attempting to get viable process requests.")
            if not isinstance(viable_requests['data'], list):
                logging.warning("Error: Malformed response from ReFlow server attempting to get viable process requests.")

            if len(viable_requests['data']) > 0:
                for request in viable_requests['data']:
                    # request ProcessRequest assignment
                    try:
                        assignment_response = rest.request_process_request_assignment(self.host, self.token, request['id'])
                    except Exception as e:
                        logging.warning("Exception: ", e.message)

                    # check the response,
                    # if 201 then our assignment request was granted and
                    # we'll verify we have the assignment
                    try:
                        if assignment_response['status'] == 201:
                            verify_assignment_response = rest.verify_process_request_assignment(self.host, self.token, request['id'])
                            if verify_assignment_response['data']['assignment'] is True:
                                pr_response = rest.get_process_request(self.host, self.token, request['id'])
                                self.__assigned_pr = pr_response['data']
                    except Exception as e:
                        logging.warning("Exception: ", e.message)
            else:
                time.sleep(self.sleep)
        else:
            # We've got something to do!

            are_inputs_valid = self.validate_inputs()

            if not are_inputs_valid:
                # TODO: Report an error for this PR back to ReFlow host
                logging.warning("Error: Invalid input values for process request")
                return

            # TODO: Next, download the samples in the sample set

            # Process the data
            self.process()

            # TODO: Verify assignment once again

            # TODO: Upload results

            # TODO: Report the ProcessRequest is complete

            # TODO: Verify 'Complete' status

            # TODO: Clean up! Delete the local files

            # afterward, delete assignment
            self.__assigned_pr = None

    @abc.abstractmethod
    def validate_inputs(self):
        """
        Override this method when subclassing Worker.
        It will be called after when the Worker has an assigned ProcessRequest.
        Returns True if the inputs are valid, else returns False
        """
        return False

    @abc.abstractmethod
    def process(self):
        """
        Override this method when subclassing Worker.
        It will be called after when the Worker has an assigned ProcessRequest.
        """
        return


