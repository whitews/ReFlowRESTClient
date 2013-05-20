import getpass
import sys
import json
from reflowrestclient.utils import *

host = "localhost:8000"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = login(host, username, password)

if token:
    print "Authentication successful"
    print '=' * 40
else:
    print "No token for you!!!"
    sys.exit()


def start():
    # Projects
    project_list = get_projects(host, token)

    for i, result in enumerate(project_list['data']):
        print i, ':', result['project_name']

    project_choice = raw_input('Choose Project:')
    project = project_list['data'][int(project_choice)]

    # Subjects
    subject_list = get_subjects(host, token, project_pk=project['id'])

    for i, result in enumerate(subject_list['data']):
        print i, ':', result['subject_id']

    subject_choice = raw_input('Choose Subject (leave blank for all subjects): ')
    subject = None
    if subject_choice:
        subject = subject_list['data'][int(subject_choice)]

    # Sites
    site_list = get_sites(host, token, project_pk=project['id'])

    if not site_list:
        sys.exit('There are no sites')

    for i, result in enumerate(site_list['data']):
        print i, ':', result['site_name']

    site_choice = raw_input('Choose Site (required): ')
    site = site_list['data'][int(site_choice)]


    # Samples
    sample_args = [host, token]
    sample_kwargs = {'site_pk': site['id']}
    if subject:
        sample_kwargs['subject_pk'] = subject['id']
    sample_list = get_samples(*sample_args, **sample_kwargs)

    if not sample_list:
        sys.exit('There are no samples')

    for i, result in enumerate(sample_list['data']):
        print i, ':', result['original_filename']

    sample_choice = raw_input('Choose Sample (leave blank for all samples): ')
    sample = None
    if sample_choice:
        sample = sample_list['data'][int(sample_choice)]


    # Compensation
    compensation_list = get_compensations(host, token, site_pk=site['id'], project_pk=project['id'])

    if not compensation_list:
        sys.exit('There are no compensations')
    for i, result in enumerate(compensation_list['data']):
        print i, ':', result['original_filename']

    compensation_choice = raw_input('Choose Compensation (required): ')
    compensation = compensation_list['data'][int(compensation_choice)]

    # Now have user verify information
    print '=' * 40
    print 'You chose to add this compensation to these samples:'

    print '\Compensation: %s' % compensation['original_filename']

    print 'Samples:'
    if sample:
        print '\t%s' % sample['original_filename']
    else:
        for s in sample_list['data']:
            print '\t%s' % s['original_filename']
    print '=' * 40

    apply_choice = None
    while apply_choice not in ['continue', 'exit']:
        apply_choice = raw_input("Type 'continue' to upload, 'exit' abort: ")
        if apply_choice == 'exit':
            sys.exit()

    print 'continue'

    if sample:
        response_dict = add_compensation_to_sample(
            host,
            token,
            sample_pk=str(sample['id']),
            compensation_pk=str(compensation['id'])
        )

        print "Response: ", response_dict['status'], response_dict['reason']
        print 'Data: '
        print json.dumps(response_dict['data'], indent=4)

    else:
        for sample in sample_list['data']:
            response_dict = add_compensation_to_sample(
                host,
                token,
                sample_pk=str(sample['id']),
                compensation_pk=str(compensation['id']),
            )

            print "Response: ", response_dict['status'], response_dict['reason']
            print 'Data: '
            print json.dumps(response_dict['data'], indent=4)

while True:
    start()