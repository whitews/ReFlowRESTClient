import reflowrestclient.utils as Rest
import json
import csv
import sys
import os
import re
import time
import getpass

if not len(sys.argv) == 2:
    sys.exit("Provide an input file")

input_file = sys.argv[1]

host = raw_input('Host: ')
username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = Rest.get_token(host, username, password)

project_pk = None  # replace with project PK
project_panels = [
    # define project panel names here
]


class CompFile(object):
    def __init__(self, f):
        self.file = f
        self.file_path = f.name
        self.file_name = os.path.basename(f.name)

        self.status = 'Pending'  # other values are 'Error' and 'Complete'
        self.error_msg = ""

        self.project = None
        self.project_pk = None

        self.project_panel = None
        self.project_panel_pk = None

        self.site_panel = None
        self.site_panel_pk = None

        self.name = None

        self.acq_date = None

        file_lines = self.file.read()
        file_lines = file_lines.splitlines(False)
        matrix_lines = list()
        found_start = False
        for i, line in enumerate(file_lines):
            if re.search('^\d', line):
                if not found_start:
                    # this is the first line that starts with a digit
                    # get the line before it to get the header text
                    # and make sure it's not the first line else there is no
                    # previous line
                    if i > 0:
                        found_start = True
                        matrix_lines.append(file_lines[i-1])
                        matrix_lines.append(line)
                elif found_start:
                    matrix_lines.append(line)
            elif found_start:
                # we've already traversed all the lines starting with digits
                # so if we get here, we've got all the matrix lines
                break

        self.matrix_text = "\n".join(matrix_lines)

    def is_site_panel_match(self, reflow_host, reflow_token, site_panel_pk):
        # Get site panel required text and compare to comp headers
        pass

    def upload(self, reflow_host, reflow_token):
        if not self.site_panel_pk or \
                not self.acq_date or \
                not self.name or \
                not self.matrix_text:
            return False

        try:
            response_dict = Rest.post_compensation(
                reflow_host,
                reflow_token,
                self.name,
                self.site_panel_pk,
                self.acq_date,
                self.matrix_text
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

site_panels = Rest.get_site_panels(host, token, project_pk=project_pk)['data']

comp_list = list()

with open(input_file, 'rb') as csv_file:
    reader = csv.reader(csv_file, delimiter='\t')
    for row in reader:
        print "Reading %s" % os.path.basename(row[0])
        acq_date = row[1]

        # get all samples matching the project and acq date
        samples = Rest.get_samples(
            host,
            token,
            project_pk=project_pk,
            acquisition_date=acq_date)['data']

        # get the distinct site panels for the samples
        site_panels = dict()
        for sample in samples:
            if sample['panel_name'] in project_panels:
                sample_sp_id = sample['site_panel']
                site_panels[sample['site_panel']] = sample['panel_name']

        # create a comp matrix for each matching site panel
        for sp in site_panels:
            comp_object = CompFile(open(row[0]))
            comp_object.acq_date = acq_date
            comp_object.name = site_panels[sp] + \
                " (" + str(sp) + ") " + \
                acq_date
            comp_object.site_panel_pk = sp

            comp_list.append(comp_object)

print "\nCreating %d compensation instances\n" % len(comp_list)
time.sleep(2)

for comp in comp_list:
    print "Uploading %s as %s" % (comp.file_name, comp.name)
    comp.upload(host, token)
