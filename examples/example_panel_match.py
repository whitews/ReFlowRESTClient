import reflowrestclient.utils as rest
import getpass

host = raw_input('Host: ')
username = raw_input('Username: ')
password = getpass.getpass('Password: ')

token = rest.get_token(host, username, password)

param_dict = {
    1: {'n': 'FSC-A', 's': ''},
    2: {'n': 'FSC-H', 's': ''},
    3: {'n': 'FSC-W', 's': ''},
    4: {'n': 'SSC-A', 's': ''},
    5: {'n': 'SSC-H', 's': ''},
    6: {'n': 'SSC-W', 's': ''},
    7: {'n': 'Blue B-A', 's': 'CD4 FITC'},
    8: {'n': 'Blue A-A', 's': ''},
    9: {'n': 'Violet H-A', 's': 'CD14 PB vAmine'},
    10: {'n': 'Violet G-A', 's': 'CD3 AmCyan'},
    11: {'n': 'Violet F-A', 's': ''},
    12: {'n': 'Violet E-A', 's': ''},
    13: {'n': 'Violet D-A', 's': ''},
    14: {'n': 'Violet C-A', 's': ''},
    15: {'n': 'Violet B-A', 's': ''},
    16: {'n': 'Violet A-A', 's': ''},
    17: {'n': 'Red C-A', 's': 'CD25 APC'},
    18: {'n': 'Red B-A', 's': ''},
    19: {'n': 'Red A-A', 's': ''},
    20: {'n': 'Green E-A', 's': 'Foxp3 PE'},
    21: {'n': 'Green D-A', 's': ''},
    22: {'n': 'Green C-A', 's': 'CD127 PE Cy5'},
    23: {'n': 'Green B-A', 's': ''},
    24: {'s': u'CD39 PE Cy7', 'n': u'Green A-A'},
    25: {'n': 'Time', 's': ''}
}

result = rest.is_site_panel_match(host, token, 1, param_dict)

print result
