import getpass
from reflowrestclient.utils import login

host = "localhost:8000"

username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = login(host, username, password)
print token

if token:
    print "Got token!!!"
else:
    print "No token for you!!!"