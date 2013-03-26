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


def get_request(token, url, params=None):
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

    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
    except Exception, e:
        print e.__class__
        return {'status': None, 'reason': 'No response', 'data': ''}

    if response.status_code == 200:
        try:
            data = response.json()
        except Exception, e:
            data = response.text()
            print e
    else:
        data = response.text

    return {
        'status': response.status_code,
        'reason': response.reason,
        'data': data,
    }


def login(host, username, password):
    """
    Login to host url using user credentials given.

    Returns the authenticating user's token (string) if successful, returns None if login failed.
    """
    url = 'https://%s%s' % (host, URLS['TOKEN'])

    token = None

    data = {
        'username': username,
        'password': password,
    }

    try:
        response = requests.post(url, data=data, verify=False)
    except Exception, e:
        print e.__class__
        return {'status': None, 'reason': 'No response', 'data': ''}

    if response.status_code == 200:
        try:
            data = response.json()
            print data
            if 'token' in data:
                token = data['token']
                # delete all the user credentials
                del(data, response, username, password)
            else:
                raise Exception("Authentication token not in response")

        except Exception, e:
            print e
    else:
        print "Authentication failed (%s: %s)" % (response.status_code, response.reason)

    return token


def get_projects(host, token, project_name=None):
    url = 'https://%s%s' % (host, URLS['PROJECTS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if project_name is not None:
        filter_params['project_name'] = project_name

    return get_request(token, url, filter_params)


def get_project(host, token, project_pk):
    """
    GET a serialized Project instance
        project_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary (JSON) representation of the Project object successfully GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['PROJECTS'], project_pk)
    return get_request(token, url)


def get_visit_types(host, token, visit_type_name=None, project_pk=None):
    url = 'https://%s%s' % (host, URLS['VISIT_TYPES'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if visit_type_name is not None:
        filter_params['visit_type_name'] = visit_type_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_visit_type(host, token, visit_type_pk):
    """
    GET a serialized ProjectVisitType instance
        visit_type_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of ProjectVisitType object GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['VISIT_TYPES'], visit_type_pk)
    return get_request(token, url)


def get_sites(host, token, site_name=None, project_pk=None):
    url = 'https://%s%s' % (host, URLS['SITES'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if site_name is not None:
        filter_params['site_name'] = site_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_site(host, token, site_pk):
    """
    GET a serialized Site instance
        site_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of Site object GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['SITES'], site_pk)
    return get_request(token, url)


def get_subjects(host, token, subject_id=None, project_pk=None):
    url = 'https://%s%s' % (host, URLS['SUBJECTS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if subject_id is not None:
        filter_params['subject_id'] = subject_id

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_subject(host, token, subject_pk):
    """
    GET a serialized Subject instance
        subject_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of Subject object GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['SUBJECTS'], subject_pk)
    return get_request(token, url)


def get_panels(host, token, panel_name=None, site_pk=None, project_pk=None):
    url = 'https://%s%s' % (host, URLS['PANELS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if panel_name is not None:
        filter_params['panel_name'] = panel_name

    if site_pk is not None:
        filter_params['site'] = site_pk

    if project_pk is not None:
        filter_params['site__project'] = project_pk

    return get_request(token, url, filter_params)


def get_panel(host, token, panel_pk):
    """
    GET a serialized Panel instance
        panel_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of Panel object GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['PANELS'], panel_pk)
    return get_request(token, url)


def get_compensations(host, token, original_filename=None, site_pk=None, project_pk=None):
    url = 'https://%s%s' % (host, URLS['COMPENSATIONS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if original_filename is not None:
        filter_params['original_filename'] = original_filename

    if site_pk is not None:
        filter_params['site'] = site_pk

    if project_pk is not None:
        filter_params['site__project'] = project_pk

    return get_request(token, url, filter_params)


def get_compensation(host, token, compensation_pk):
    """
    GET a serialized Compensation instance
        compensation_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of Compensation object GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['COMPENSATIONS'], compensation_pk)
    return get_request(token, url)


def get_parameters(host, token, name=None, parameter_type=None, name_contains=None):
    url = 'https://%s%s' % (host, URLS['PARAMETERS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if name is not None:
        filter_params['parameter_short_name'] = name

    if name_contains is not None:
        filter_params['name_contains'] = name_contains

    if type is not None:
        filter_params['parameter_type'] = parameter_type

    return get_request(token, url, filter_params)


def get_parameter(host, token, parameter_pk):
    """
    GET a serialized Parameter instance
        compensation_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of Parameter object GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['PARAMETERS'], parameter_pk)
    return get_request(token, url)


def get_samples(host, token, subject_pk=None, site_pk=None, project_pk=None, visit_pk=None, parameter_names=None):
    url = 'https://%s%s' % (host, URLS['SAMPLES'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if subject_pk is not None:
        filter_params['subject'] = subject_pk

    if site_pk is not None:
        filter_params['site'] = site_pk

    if project_pk is not None:
        filter_params['subject__project'] = project_pk

    if visit_pk is not None:
        filter_params['visit'] = visit_pk

    if parameter_names is not None:
        filter_params['parameter_names'] = parameter_names

    return get_request(token, url, filter_params)


def get_sample(host, token, sample_pk):
    """
    GET a serialized Sample instance
        sample_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of Sample object GET'd, empty string if unsuccessful
    """
    url = 'https://%s%s%s/' % (host, URLS['SAMPLES'], sample_pk)
    return get_request(token, url)


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

    url = 'https://%s%s' % (host, URLS['SAMPLES'])
    headers = {'Authorization': "Token %s" % token}

    # Subject is required
    data = {'subject': subject_pk}

    # add the site field if present
    if site_pk:
        data['site'] = site_pk

    # add the visit_type field if present
    if visit_type_pk:
        data['visit'] = visit_type_pk

    # add the panel field if present
    if panel_pk:
        data['panel'] = panel_pk

    # get FCS file
    files = {
        'sample_file': open(file_path, "rb")
    }

    try:
        response = requests.post(url, headers=headers, data=data, files=files, verify=False)
    except Exception, e:
        print e.__class__
        return {'status': None, 'reason': 'No response', 'data': ''}

    if response.status_code == 201:
        try:
            data = response.json()
        except Exception, e:
            data = response.text()
            print e
    else:
        data = response.text

    return {
        'status': response.status_code,
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