import getpass
import sys
import reflowrestclient.utils as rest
import time
import os

host = raw_input('Host: ')
username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = rest.login(host, username, password)

if token:
    print "Authentication successful"
    print '=' * 40
else:
    print "No token for you!!!"
    sys.exit()

start_time = time.time()
responses = rest.download_samples(
    host,
    token,
    sample_pk_list=[1,2,3,4,5,6,7,8,9,10])
end_time = time.time()

stats_01 = os.stat("1.fcs")
stats_02 = os.stat("2.fcs")
stats_03 = os.stat("3.fcs")
stats_04 = os.stat("4.fcs")
stats_05 = os.stat("5.fcs")
stats_06 = os.stat("6.fcs")
stats_07 = os.stat("7.fcs")
stats_08 = os.stat("8.fcs")
stats_09 = os.stat("9.fcs")
stats_10 = os.stat("10.fcs")

total_size = \
    stats_01.st_size + \
    stats_02.st_size + \
    stats_03.st_size + \
    stats_04.st_size + \
    stats_05.st_size + \
    stats_06.st_size + \
    stats_07.st_size + \
    stats_08.st_size + \
    stats_09.st_size + \
    stats_10.st_size
mbps = ((total_size * 8) / 1024 / 1024) / (end_time - start_time)
mbps = round(mbps, 3)

for r in responses:
    print r
print total_size
print end_time - start_time
print str(mbps) + ' Mbps'