import getpass
import sys
import json
from reflowrestclient.utils import *
import fcm

file_path_list = sys.argv[1:]

print 'Verifying FCS files...'

for file_path in file_path_list:
    try:
        f = fcm.loadFCS(file_path)
        if not len(f.channels) > 0:
            raise Exception("One of more files specified either isn't an FCS file or has no channel information.")
    except Exception, e:
        print e
        sys.exit()

host = raw_input('Host: ')
username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = get_token(host, username, password)

if token:
    print "Authentication successful"
    print '=' * 40
else:
    print "No token for you!!!"
    sys.exit()


# Projects
project_list = get_projects(host, token)

for i, result in enumerate(project_list['data']):
    print i, ':', result['project_name']

project_choice = raw_input('Choose Project:')
project = project_list['data'][int(project_choice)]


# Visits
visit_type_list = get_visit_types(host, token, project_pk=project['id'])

for i, result in enumerate(visit_type_list['data']):
    print i, ':', result['visit_type_name']

visit_type_choice = raw_input('Choose Visit Type: ')
visit_type = visit_type_list['data'][int(visit_type_choice)]


# Subjects
subject_list = get_subjects(host, token, project_pk=project['id'])

for i, result in enumerate(subject_list['data']):
    print i, ':', result['subject_id']

subject_choice = raw_input('Choose Subject: ')
subject = subject_list['data'][int(subject_choice)]


# Sites
site_list = get_sites(host, token, project_pk=project['id'])

for i, result in enumerate(site_list['data']):
    print i, ':', result['site_name']

site_choice = raw_input('Choose Site: ')
site = site_list['data'][int(site_choice)]

# Now have user verify information
print '=' * 40
print 'The following files will be uploaded:'

for file_path in file_path_list:
    print '\t%s' % file_path

print 'Using this information:'
print '\tProject: %s' % project['project_name']
print '\tVisit Type: %s' % visit_type['visit_type_name']
print '\tSubject: %s' % subject['subject_id']
print '\tSite: %s' % site['site_name']
print '=' * 40

upload_choice = None
while upload_choice not in ['continue', 'exit']:
    upload_choice = raw_input("Type 'continue' to upload, 'exit' abort: ")
    if upload_choice == 'exit':
        sys.exit()

print 'continue'

for file_path in file_path_list:

    response_dict = post_sample(
        host,
        token,
        file_path,
        subject_pk=str(subject['id']),
        site_pk=str(site['id']),
        visit_type_pk=str(visit_type['id'])
    )

    print "Response: ", response_dict['status'], response_dict['reason']
    print 'Data: '
    print json.dumps(response_dict['data'], indent=4)
