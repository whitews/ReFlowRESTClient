import getpass
import sys
import io
import base64
from reflowrestclient.utils import *
import numpy

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

response_dict = get_sample_data(host, token, sample_pk=1)

decoded_data = base64.decodestring(response_dict['data']['channel_data'])
numpy_array = numpy.load(io.BytesIO(decoded_data))
print numpy_array.shape
