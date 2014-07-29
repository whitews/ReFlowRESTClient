import getpass
from reflowrestclient.utils import get_token, METHOD

host = "localhost:8000"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')
method = raw_input('Method (https or http): ')

token = get_token(host, username, password, method=METHOD[method])

if token:
    print "Got token!!!"
else:
    print "No token for you!!!"