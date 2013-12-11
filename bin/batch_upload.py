import reflowrestclient.utils as Rest
import flowio
import json
import csv
import sys
import os
import re
import hashlib

if not len(sys.argv) == 2:
    sys.exit("Provide an input file")

input_file = sys.argv[1]

host = '127.0.0.1'
token = 'replace-me-with-a-real-token'

project_pk = None  # replace with project PK
site_pk = None  # replace with project PK
visit_pk = None  # replace with project PK
specimen_pk = None  # replace with project PK
pretreatment = 'In vitro'  # change if necessary
storage = 'Cryopreserved'  # change if necessary
cytometer_pk = None  # replace with project PK


class FCSFile(object):
    def __init__(self, fcs_file):
        self.file_path = fcs_file.name
        self.file_name = os.path.basename(fcs_file.name)
        hash_obj = hashlib.sha1(fcs_file.read())
        self.file_hash = hash_obj.hexdigest()
        fcs_file.seek(0)

        # test if file is an FCS file, raise TypeError if not
        try:
            self.metadata = flowio.FlowData(fcs_file).text
        except:
            raise TypeError("File %s is not an FCS file." % self.file_name)

        self.status = 'Pending'  # other values are 'Error' and 'Complete'
        self.error_msg = ""

        self.project = None
        self.project_pk = None

        self.subject = None
        self.subject_pk = None

        self.visit = None
        self.visit_pk = None

        self.specimen = None
        self.specimen_pk = None

        self.stimulation = None
        self.stimulation_pk = None

        self.pretreatment = None

        self.storage = None

        self.project_panel = None
        self.project_panel_pk = None

        self.site_panel = None
        self.site_panel_pk = None

        self.cytometer = None
        self.cytometer_pk = None

        self.acq_date = None

    def is_site_panel_match(self, reflow_host, reflow_token, site_panel_pk):
        param_dict = {}
        for key in self.metadata:
            key_matches = re.search('^P(\d+)([N,S])$', key, flags=re.IGNORECASE)
            if key_matches:
                channel_number = int(key_matches.group(1))
                n_or_s = str.lower(key_matches.group(2))
                if not channel_number in param_dict:
                    param_dict[channel_number] = {}
                param_dict[channel_number][n_or_s] = self.metadata[key]
        return Rest.is_site_panel_match(
            reflow_host,
            reflow_token,
            site_panel_pk,
            param_dict)

    def exists_in_project(self, reflow_host, reflow_token, reflow_project_pk):
        try:
            response = Rest.get_samples(
                reflow_host,
                reflow_token,
                project_pk=reflow_project_pk,
                sha1=self.file_hash)
        except:
            print "Bad stuff happened on the way to get the file hash"
            return False

        if response:
            if 'data' in response:
                if len(response['data']) > 0:
                    return True
        return False

    def upload(self, reflow_host, reflow_token):
        if not self.subject_pk or \
                not self.site_panel_pk or \
                not self.cytometer_pk or \
                not self.visit_pk or \
                not self.specimen_pk or \
                not self.pretreatment or \
                not self.storage or \
                not self.acq_date or \
                not self.file_path or \
                not self.stimulation_pk:
            return False

        rest_args = [
            reflow_host,
            reflow_token,
            self.file_path
        ]
        rest_kwargs = {
            'subject_pk': str(self.subject_pk),
            'site_panel_pk': str(self.site_panel_pk),
            'cytometer_pk': str(self.cytometer_pk),
            'visit_type_pk': str(self.visit_pk),
            'specimen_pk': str(self.specimen_pk),
            'pretreatment': str(self.pretreatment),
            'storage': str(self.storage),
            'stimulation_pk': str(self.stimulation_pk),
            'acquisition_date': str(self.acq_date)
        }

        try:
            response_dict = Rest.post_sample(
                *rest_args,
                **rest_kwargs
            )
        except Exception, e:
            print e
            return False

        if response_dict['status'] == 201:
            self.status = 'Complete'
        elif response_dict['status'] == 400:
            self.error_msg = "\n".join(
                json.loads(response_dict['data']).values()[0])
            print self.error_msg
            self.status = 'Error'
        else:
            self.status = 'Error'

subject_dict = dict()
subjects = Rest.get_subjects(host, token, project_pk=project_pk)
if 'data' in subjects:
    for subject in subjects['data']:
        subject_dict[subject['subject_code']] = subject['id']
else:
    sys.exit('Server reported no subjects')

site_panels = Rest.get_site_panels(host, token, project_pk=project_pk)['data']
stimulations = Rest.get_stimulations(host, token, project_pk=project_pk)['data']

with open(input_file, 'rb') as csv_file:
    reader = csv.reader(csv_file, delimiter='\t')
    for row in reader:
        if row[2] not in subject_dict:
            print "Subject %s not found %s" % (
                row[2], os.path.basename(row[0]))
            continue
        print "Reading %s" % os.path.basename(row[0])

        f = open(row[0])
        fcs_obj = FCSFile(f)
        f.close()

        fcs_obj.acq_date = row[1]
        fcs_obj.subject = row[2]
        fcs_obj.stimulation = row[3]
        fcs_obj.project_panel = row[4]

        already_uploaded = fcs_obj.exists_in_project(
            reflow_host=host,
            reflow_token=token,
            reflow_project_pk=project_pk)

        if already_uploaded:
            print "\tFile already uploaded: %s, %s" % (
                fcs_obj.file_name,
                fcs_obj.acq_date)
            continue

        fcs_obj.project_pk = project_pk
        fcs_obj.visit_pk = visit_pk
        fcs_obj.pretreatment = pretreatment
        fcs_obj.storage = storage
        fcs_obj.cytometer_pk = cytometer_pk
        fcs_obj.specimen_pk = specimen_pk

        # determine subject_pk
        if fcs_obj.subject in subject_dict:
            fcs_obj.subject_pk = subject_dict[fcs_obj.subject]
        if not fcs_obj.subject_pk:
            print "\tSubject not found: %s, %s" % (
                fcs_obj.file_name,
                fcs_obj.acq_date)
            continue

        # determine site_panel_pk
        skip = False
        while not skip:
            for site_panel in site_panels:
                if site_panel['project_panel_name'] == fcs_obj.project_panel:
                    if fcs_obj.is_site_panel_match(host, token, site_panel['id']):
                        fcs_obj.site_panel_pk = site_panel['id']
                        break
            if not fcs_obj.site_panel_pk:
                print "\tSite panel not found: %s, %s" % (
                    fcs_obj.file_name,
                    fcs_obj.acq_date)
                print \
                    "Pausing script, hit enter to try again, " + \
                    "type 'skip' to ignore this file: "
                user_input = raw_input()
                if user_input == 'skip':
                    skip = True
                    continue
                print "Re-building site panel list..."
                site_panels = Rest.get_site_panels(
                    host,
                    token,
                    project_pk=project_pk)['data']
            else:
                break  # it was found so exit the while loop

        if skip:
            continue

        # determine stimulation_pk
        for stim in stimulations:
            if stim['stimulation_name'] == fcs_obj.stimulation:
                fcs_obj.stimulation_pk = stim['id']
        if not fcs_obj.stimulation_pk:
            print "Stimulation not found for %s, %s" % (
                fcs_obj.file_name, fcs_obj.acq_date)
            continue

        # finally, upload the file
        print "\tUploading %s..." % fcs_obj.file_name
        fcs_obj.upload(host, token)