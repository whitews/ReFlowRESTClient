import httplib
import json
import urllib
import requests
import os
import re

BOUNDARY = '--------Boundary'
URLS = {
    'TOKEN': '/api-token-auth/',
    'PROJECTS': '/api/projects/',
    'SITES': '/api/sites/',
    'SUBJECTS': '/api/subjects/',
    'PANELS': '/api/panels/',
    'COMPENSATIONS': '/api/compensations/',
    'PARAMETERS': '/api/parameters/',
    'SAMPLES': '/api/samples/',
    'VISIT_TYPES': '/api/visit_types/'
}


def get_request(host, token, url):
    """
    Returns a dictionary with the following keys:
        status: HTTP response status code
        reason: HTTP response reason
        data: A dictionary converted from JSON response data
    """

    headers = {
        'User-Agent': 'python',
        'Authorization': "Token %s" % token,
    }

    conn = httplib.HTTPSConnection(host)
    conn.request('GET', url, headers=headers)

    response = conn.getresponse()

    #headers = response.getheaders()
    if response.status == 200:
        try:
            data = json.loads(response.read())
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


def login(host, username, password):
    """
    Login to host url using user credentials given.

    Returns the authenticating user's token (string) if successful, returns None if login failed.
    """

    token = None

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

    conn = httplib.HTTPSConnection(host)
    conn.request('POST', URLS['TOKEN'], '\r\n'.join(auth_data), auth_headers)
    response = conn.getresponse()

    if response.status == 200:
        try:
            data = response.read()
            json_resp = json.loads(data)
            if 'token' in json_resp:
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
    url = URLS['PROJECTS']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if project_name is not None:
        filter_params.append(urllib.urlencode({'project_name': project_name}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def get_visit_types(host, token, visit_type_name=None, project_pk=None):
    url = URLS['VISIT_TYPES']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if visit_type_name is not None:
        filter_params.append(urllib.urlencode({'visit_type_name': visit_type_name}))

    if project_pk is not None:
        filter_params.append(urllib.urlencode({'project': project_pk}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def get_sites(host, token, site_name=None, project_pk=None):
    url = URLS['SITES']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if site_name is not None:
        filter_params.append(urllib.urlencode({'site_name': site_name}))

    if project_pk is not None:
        filter_params.append(urllib.urlencode({'project': project_pk}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def get_subjects(host, token, subject_id=None, project_pk=None):
    url = URLS['SUBJECTS']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if subject_id is not None:
        filter_params.append(urllib.urlencode({'subject_id': subject_id}))

    if project_pk is not None:
        filter_params.append(urllib.urlencode({'project': project_pk}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def get_panels(host, token, panel_name=None, site_pk=None, project_pk=None):
    url = URLS['PANELS']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if panel_name is not None:
        filter_params.append(urllib.urlencode({'panel_name': panel_name}))

    if site_pk is not None:
        filter_params.append(urllib.urlencode({'site': site_pk}))

    if project_pk is not None:
        filter_params.append(urllib.urlencode({'site__project': project_pk}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def get_compensations(host, token, original_filename=None, site_pk=None, project_pk=None):
    url = URLS['COMPENSATIONS']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if original_filename is not None:
        filter_params.append(urllib.urlencode({'original_filename': original_filename}))

    if site_pk is not None:
        filter_params.append(urllib.urlencode({'site': site_pk}))

    if project_pk is not None:
        filter_params.append(urllib.urlencode({'site__project': project_pk}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def get_parameters(host, token, name=None, parameter_type=None, name_contains=None):
    url = URLS['PARAMETERS']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if name is not None:
        filter_params.append(urllib.urlencode({'parameter_short_name': name}))

    if name_contains is not None:
        filter_params.append(urllib.urlencode({'name_contains': name_contains}))

    if type is not None:
        filter_params.append(urllib.urlencode({'parameter_type': parameter_type}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def get_samples(host, token, subject_pk=None, site_pk=None, project_pk=None, visit_pk=None, parameter_names=None):
    url = URLS['SAMPLES']
    filter_params = list()
    filter_params.append(urllib.urlencode({'paginate_by': '0'}))

    if subject_pk is not None:
        filter_params.append(urllib.urlencode({'subject': subject_pk}))

    if site_pk is not None:
        filter_params.append(urllib.urlencode({'site': site_pk}))

    if project_pk is not None:
        filter_params.append(urllib.urlencode({'subject__project': project_pk}))

    if visit_pk is not None:
        filter_params.append(urllib.urlencode({'visit': visit_pk}))

    if parameter_names is not None:
        filter_params.append(urllib.urlencode({'parameter_names': parameter_names}))

    if len(filter_params) > 0:
        filter_string = "&".join(filter_params)
        url = "?".join([url, filter_string])

    return get_request(host, token, url)


def download_sample(host, token, sample_pk=None, filename=None, directory=None):
    if sample_pk is not None:
        url = "https://%s/api/samples/%d/download/" % (host, sample_pk)
    else:
        return 'sample_pk is required'

    headers = {'Authorization': "Token %s" % token}
    data = ''
    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception, e:
        print e.__class__
        return {'status': None, 'reason': 'No response', 'data': data}

    if r.status_code == 200:
        try:
            if filename is None:
                filename = re.findall("filename=([^']+)", r.headers['content-disposition'])
            if directory is None:
                directory = os.getcwd()

            with open("%s/%s" % (directory, filename[0]), "wb") as fcs_file:
                fcs_file.write(r.content)
        except Exception, e:
            print e
    else:
        data = r.text

    return {
        'status': r.status_code,
        'reason': r.reason,
        'data': data,
    }


def post_sample(host, token, file_path=None, subject_pk=None, site_pk=None, visit_type_pk=None, panel_pk=None):
    """
    POST a FCS sample, associating the file with the following:
        subject    (required)
        site       (optional)
        visit_type (optional)
        panel      (optional)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': JSON string representation of the Sample object successfully posted, empty string if unsuccessful
    """

    post_sample_url = '/api/samples/'
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
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
        body.append('Content-Disposition: form-data; name="visit"')
        body.append('')
        body.append(visit_type_pk)
    
    # add the panel field if present
    if panel_pk:
        body.append('--%s' % BOUNDARY)
        body.append('Content-Disposition: form-data; name="panel"')
        body.append('')
        body.append(panel_pk)

    # get FCS file and append to body
    file_obj = open(file_path, "rb")
    filename = file_obj.name.split('/')[-1]
    body.append('--%s' % BOUNDARY)
    body.append('Content-Disposition: form-data; name="sample_file"; filename="%s"' % filename)
    body.append('Content-Type: application/octet-stream')
    file_obj.seek(0)
    body.append('')
    body.append(file_obj.read())
    file_obj.close()
    body.append('--' + BOUNDARY + '--')
    body.append('')

    body = '\r\n'.join(body)

    conn = httplib.HTTPSConnection(host)
    #conn.set_debuglevel(1)
    headers = {
        'User-Agent': 'python',
        'Authorization': "Token %s" % token,
        'Content-Type': content_type,
        'Content-Length': str(len(body)),
        'Connection': 'keep-alive',
    }

    conn.request('POST', post_sample_url, body, headers)
    try:
        response = conn.getresponse()
    except Exception, e:
        print e.__class__
        return {'status': None, 'reason': 'No response', 'data': ''}
    if response.status == 201:
        try:
            resp = response.read()
        except:
            return {'status': response.status, 'reason': 'Could not read response', 'data': ''}
        try:
            data = json.loads(resp)
        except Exception, e:
            data = resp
            print e
    else:
        data = response.read()

    return {
        'status': response.status,
        'reason': response.reason,
        'data': data,
    }


def patch_sample_with_panel(host, token, sample_pk, panel_pk):
    """
    PATCH a FCS sample, creating sample parameters based on a panel
        sample_pk    (required)
        panel_pk     (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary (JSON) representation of the Sample object successfully PATCH'd, empty string if unsuccessful
    """
    if not sample_pk and panel_pk:
        return ''

    url = 'https://%s/api/samples/%s/apply_panel/' % (host, sample_pk)
    headers = {'Authorization': "Token %s" % token}

    try:
        r = requests.patch(url, data={'panel': panel_pk}, headers=headers, verify=False)
    except Exception, e:
        print e.__class__
        return {'status': None, 'reason': 'No response', 'data': ''}

    if r.status_code == 201:
        try:
            data = r.json()
        except Exception, e:
            data = r.text()
            print e
    else:
        data = r.text

    return {
        'status': r.status_code,
        'reason': r.reason,
        'data': data,
    }


def add_compensation_to_sample(host, token, sample_pk, compensation_pk):
    """
    POST a SampleCompensationMap
        sample_pk    (required)
        compensation_pk     (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary (JSON) representation of the SampleCompensationMap object successfully POST'd, else ''
    """
    if not sample_pk and compensation_pk:
        return ''

    url = 'https://%s/api/samples/%s/add_compensation/' % (host, sample_pk)
    headers = {'Authorization': "Token %s" % token}

    data = {
        'compensation': compensation_pk,
        'sample': sample_pk
    }

    try:
        r = requests.post(url, data=data, headers=headers, verify=False)
    except Exception, e:
        print e.__class__
        return {'status': None, 'reason': 'No response', 'data': ''}

    if r.status_code == 201:
        try:
            data = r.json()
        except Exception, e:
            data = r.text()
            print e
    else:
        data = r.text

    return {
        'status': r.status_code,
        'reason': r.reason,
        'data': data,
    }