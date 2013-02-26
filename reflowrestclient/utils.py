import httplib
import os
import stat
import json
import urllib

BOUNDARY = '----Boundary'

def login(host, username, password):
    """
    Login to host url using user credentials given.

    Returns the authenticating user's token (string) if successful, returns None if login failed.
    """

    token = None
    url = "/api-token-auth/"

    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

    auth_headers = {
        'User-Agent': 'python',
        'Content-Type': content_type,
    }

    auth_data = [
        '--%s' % BOUNDARY,
        'Content-Disposition: form-data; name="username"',
        '',
        username,
        '--%s' % BOUNDARY,
        'Content-Disposition: form-data; name="password"',
        '',
        password,
        '--' + BOUNDARY + '--',
        '',
    ]

    conn = httplib.HTTPConnection(host)
    conn.request('POST', url, '\r\n'.join(auth_data), auth_headers)
    response = conn.getresponse()

    if response.status == 200:
        try:
            data = response.read()
            json_resp = json.loads(data)
            if json_resp.has_key('token'):
                token = json_resp['token']
                # delete all the user credentials
                del(data, json_resp, response, username, password)
            else:
                raise Exception("Authentication token not in response")
        except Exception, e:
            print e
    else:
        print "Authentication failed (%s: %s)" % (response.status, response.reason)

    return token


def get_projects(host, token, project_name=None):
    project_list_url = '/api/projects/'
    filter_params = list()

    if project_name is not None:
        filter_params.append(urllib.urlencode({'project_name': project_name}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        project_list_url = "?".join([project_list_url, filter_string])

    print project_list_url

    headers = {
        'User-Agent': 'python',
        'Authorization': "Token %s" % token,
    }

    conn = httplib.HTTPConnection(host)
    conn.request('GET', project_list_url, headers=headers)

    response = conn.getresponse()
    #headers = response.getheaders()
    if response.status == 200:
        try:
            data = response.read()
        except Exception, e:
            data = ''
            print e

    else:
        data = ''

    return {
        'status': response.status,
        'reason': response.reason,
        'data': data,
    }


def post_sample(host, token, file_path=None, subject_pk=None, site_pk=None, visit_type_pk=None, panel_pk=None):
    """
    POST a FCS sample, associating the file with a subject (required), site (optional), visit_type (optional), panel (optional)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': JSON string representation of the Sample object successfully posted, empty string if unsuccessful
    """

    file_obj = open(file_path, "rb")

    post_sample_url = '/api/samples/'

    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

    headers = {
        'User-Agent': 'python',
        'Content-Type': content_type,
        'Authorization': "Token %s" % token,
    }

    body = list()

    # add the subject field and value to body
    body.append('--%s' % BOUNDARY)
    body.append('Content-Disposition: form-data; name="subject"')
    body.append('')
    body.append(subject_pk)

    # add the site field if present
    if site_pk:
        body.append('--%s' % BOUNDARY)
        body.append('Content-Disposition: form-data; name="site"')
        body.append('')
        body.append(site_pk)

    # add the visit_type field if present
    if visit_type_pk:
        body.append('--%s' % BOUNDARY)
        body.append('Content-Disposition: form-data; name="visit_type"')
        body.append('')
        body.append(visit_type_pk)
    
    # add the panel field if present
    if panel_pk:
        body.append('--%s' % BOUNDARY)
        body.append('Content-Disposition: form-data; name="panel"')
        body.append('')
        body.append(panel_pk)

    # get FCS file and append to body
    file_size = os.fstat(file_obj.fileno())[stat.ST_SIZE]  # not used now, but we may want to chunk the file if too large
    filename = file_obj.name.split('/')[-1]
    body.append('--%s' % BOUNDARY)
    body.append('Content-Disposition: form-data; name="sample_file"; filename="%s"' % filename)
    body.append('Content-Type: application/octet-stream')
    file_obj.seek(0)
    body.append('\r\n' + file_obj.read())

    body.append('--' + BOUNDARY + '--')
    body.append('')

    conn = httplib.HTTPConnection(host)
    conn.request('POST', post_sample_url, '\r\n'.join(body), headers)
    response = conn.getresponse()
    if response.status == 200:
        try:
            data = response.read()
        except Exception, e:
            data = ''
            print e

    else:
        data = ''

    return {
        'status': response.status,
        'reason': response.reason,
        'data': data,
    }
