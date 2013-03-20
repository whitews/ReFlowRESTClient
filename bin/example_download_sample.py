import getpass
import sys
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

response_dict = download_sample(host, token, sample_pk=1)
