import getpass
import sys
import reflowrestclient.utils as rest
import time
import os

host = raw_input('Host: ')
username = raw_input('Username: ')
password = getpass.getpass('Password: ')
filename = 'test.fcs'

token = rest.get_token(host, username, password)

if token:
    print "Authentication successful"
    print '=' * 40
else:
    print "No token for you!!!"
    sys.exit()

start_time = time.time()
response_dict = rest.download_sample(
    host,
    token,
    sample_pk=1,
    filename=filename)
end_time = time.time()

stats = os.stat(filename)
mbps = ((stats.st_size * 8) / 1024 / 1024) / (end_time - start_time)
mbps = round(mbps, 3)

print response_dict
print str(mbps) + ' Mbps'