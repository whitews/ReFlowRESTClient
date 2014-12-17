import getpass
import sys
import csv
import operator
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

pr_id = raw_input('Process Request ID: ')

response_dict = utils.get_sample_clusters(
    host,
    token,
    process_request_pk=pr_id
)

sample_cluster_list = response_dict['data']
sample_dict = {}

results = list()  # a list of rows, each row a list of values

for sc in sample_cluster_list:
    sample_pk = sc['sample']
    if not sample_pk in sample_dict.keys():
        response_dict = utils.get_sample(host, token, sample_pk=sample_pk)
        sample_dict[sample_pk] = response_dict['data']

        subject_pk = sample_dict[sample_pk]['subject']

        response_dict = utils.get_subject(host, token, subject_pk=subject_pk)
        sample_dict[sample_pk]['subject_group_name'] = response_dict['data']['subject_group_name']

        sample_dict[sample_pk]['total_events'] = 0  # start w/zero

    # keep a running total of the sample's events
    sample_dict[sample_pk]['total_events'] += len(sc['event_indices'])

    # save file name in sample cluster list for sorting
    sc['original_filename'] = str(sample_dict[sample_pk]['original_filename'])

sample_cluster_list = sorted(
    sample_cluster_list,
    key=operator.itemgetter(
        'cluster_index',
        'original_filename',
    )
)

# iterate twice so we capture the correct total # of events per sample
for sc in sample_cluster_list:
    sample_pk = sc['sample']
    row = [
        sample_dict[sample_pk]['panel_name'],          # panel template name
        sc['cluster_index'],                           # cluster index
        sc['original_filename'],                       # sample file name
        sample_dict[sample_pk]['subject_code'],        # subject code
        sample_dict[sample_pk]['subject_group_name'],  # subject group name
        len(sc['event_indices']),                      # event count
        sample_dict[sample_pk]['total_events'],        # total events
        # finally, the event percentage
        round(
            (float(len(sc['event_indices'])) / sample_dict[sample_pk]['total_events']) * 100,
            2
        )
    ]
    results.append(row)

header = [
    'panel_name',
    'cluster_index',
    'sample_file',
    'subject_code',
    'subject_group',
    'event_count',
    'total_events',
    'events (% of total)'
]

with open('pr_results_' + str(pr_id) + '.csv', 'wb') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(header)
    writer.writerows(results)