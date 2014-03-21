import getpass
import sys
from reflowrestclient import utils

host = raw_input('Host: ')
username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = utils.get_token(host, username, password)

if token:
    print "Authentication successful"
    print '=' * 40
else:
    print "No token for you!!!"
    sys.exit()

response_dict = utils.download_process_output(
    host,
    token,
    process_output_pk=75)