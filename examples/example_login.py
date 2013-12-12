import getpass
from reflowrestclient.utils import get_token

host = "localhost:8000"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = get_token(host, username, password)

if token:
    print "Got token!!!"
else:
    print "No token for you!!!"