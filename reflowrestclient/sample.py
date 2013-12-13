import os

import utils


class Sample(object):
    """
    Represents the FCS sample downloaded from a ReFlow server.
    Used by a Worker to manage downloaded samples related to a
    ReFlow ProcessRequest
    """
    def __init__(self, host, sample_dict):
        """
        host: the ReFlow host from which the sample originated
        sample_dict: the ReFlow 'data' dictionary

        Raises KeyError if sample_dict is incomplete
        """
        self.host = host
        self.sample_id = sample_dict['id']

        self.fcs_path = None  # path to downloaded FCS file
        self.fcs_comp_path = None  # path to fcs compensated data (numpy)
        self.subsample_path = None  # path to downloaded Numpy array
        self.subsample_comp_path = None  # path sub-sampled comp'd data (numpy)

        self.acquisition_date = sample_dict['acquisition_date']
        self.original_filename = sample_dict['original_filename']
        self.sha1 = sample_dict['sha1']
        self.compensation_id = sample_dict['compensation']

        self.exclude = sample_dict['exclude']

        self.site_id = sample_dict['site']
        self.site_name = sample_dict['site_name']

        self.specimen_id = sample_dict['specimen']
        self.specimen_name = sample_dict['specimen_name']

        self.stimulation_id = sample_dict['stimulation_id']
        self.stimulation_name = sample_dict['stimulation_name']

        self.visit_id = sample_dict['visit']
        self.visit_name = sample_dict['visit_name']

        self.subject_id = sample_dict['subject']
        self.subject_code = sample_dict['subject_code']

        self.project_panel_id = sample_dict['id']
        self.project_panel_name = sample_dict['panel_name']

        self.site_panel_id = sample_dict['id']

    def download_subsample(self, token):
        """
        ReFlow Worker sample downloads are kept in /var/tmp/ReFlow-data
        organized by host, then sample id

        Returns True if download succeeded or file is already present
        Also updates self.subsample_path
        """
        if not self.host or not self.sample_id:
            return False

        download_dir = '/var/tmp/ReFlow-data/' + str(self.host) + '/'
        subsample_path = download_dir + self.sample_id + '.npy'

        if not os.path.exists(subsample_path):
            try:
                utils.download_sample(
                    self.host,
                    token,
                    sample_pk=self.sample_id,
                    data_format='npy',
                    directory=download_dir)
            except Exception, e:
                print e
                return False

        self.subsample_path = subsample_path
        return True

    def compensate_subsample(self, token):
        """
        Gets compensation matrix and applies it to the subsample.

        Returns False if the subsample has not been downloaded or
        if the compensation fails

        Note: Compensation matrix is chosen in the following order:
            1st choice: self.compensation which comes from the Sample's
                        directly related compensation relationship on the
                        ReFlow host (self.host)
            2nd choice: The first matching compensation matrix on the
                        ReFlow host (self.host) which matches both the
                        Sample's site panel and the Sample's acquisition date
            3rd choice: The spillover matrix within the original FCS file
        """
        if not self.host or not self.sample_id:
            return False

        if not self.subsample_path and os.path.exists(self.subsample_path):
            return False

        download_dir = '/var/tmp/ReFlow-data/' + str(self.host) + '/comp/'

        if self.compensation_id:
            comp_path = download_dir + self.sample_id + '.npy'

            if not os.path.exists(comp_path):
                try:
                    utils.download_compensation(
                        self.host,
                        token,
                        data_format='npy',
                        directory=comp_path)
                except Exception, e:
                    print e
                    return False
        else:
            # try to find a matching compensation
            comps = utils.get_compensations(
                self.host,
                token,
                site_panel_pk=self.site_panel_id,

            )




        return True
