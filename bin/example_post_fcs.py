import getpass
import sys
import json
from reflowrestclient.utils import login, post_sample

host = "localhost:8000"
auth_token_url = "/api-token-auth/"
url = "/api/samples/"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = login(host, username, password)

if token:
    print "Got token!!!"
else:
    print "No token for you!!!"
    sys.exit()


subject_pk = raw_input('Subject Primary Key: ')
site_pk = raw_input('Site Primary Key: ')
visit_type_pk = raw_input('Visit Type Primary Key: ')
panel_pk = raw_input('Panel Primary Key: ')
file_path = raw_input('FCS File Path: ')

response_dict = post_sample(
    host,
    token,
    file_path,
    subject_pk=subject_pk,
    site_pk=site_pk,
    visit_type_pk=visit_type_pk,
    panel_pk=panel_pk
)

print "Response: ", response_dict['status'], response_dict['reason']
print 'Data: '
print json.dumps(json.loads(response_dict['data']), indent=4)