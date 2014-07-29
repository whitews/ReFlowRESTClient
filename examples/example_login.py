import getpass
from reflowrestclient import utils

host = "localhost:8000"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')
method = raw_input('Method (https or http): ')

token = utils.get_token(host, username, password, method=utils.METHOD[method])

if token:
    print "Got token!!!"
else:
    print "No token for you!!!"
