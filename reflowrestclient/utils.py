import requests
import grequests
import os
import re

METHOD = 'https://'

URLS = {
    'TOKEN': '/api/token-auth/',
    'PROJECTS': '/api/repository/projects/',
    'SPECIMENS': '/api/repository/specimens/',
    'SUBJECT_GROUPS': '/api/repository/subject_groups/',
    'SITES': '/api/repository/sites/',
    'SUBJECTS': '/api/repository/subjects/',
    'PROJECT_PANELS': '/api/repository/project_panels/',
    'SITE_PANELS': '/api/repository/site_panels/',
    'COMPENSATIONS': '/api/repository/compensations/',
    'STIMULATIONS': '/api/repository/stimulations/',
    'SAMPLES': '/api/repository/samples/',
    'CREATE_SAMPLES': '/api/repository/samples/add/',
    'VISIT_TYPES': '/api/repository/visit_types/',

    # Process manager API URLs
    'PROCESSES': '/api/process_manager/processes/',
    'WORKERS': '/api/process_manager/workers/',
    'VERIFY_WORKER': '/api/process_manager/verify_worker/',
    'PROCESS_REQUESTS': '/api/process_manager/process_requests/',
    'VIABLE_PROCESS_REQUESTS': '/api/process_manager/viable_process_requests/',
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
        response = requests.get(
            url, headers=headers, params=params, verify=False)
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

    Returns the authenticating user's token (string) if successful,
    returns None if login failed.
    """
    url = '%s%s%s' % (METHOD, host, URLS['TOKEN'])

    token = None

    data = {
        'username': username,
        'password': password,
    }

    try:
        response = requests.post(url, data=data, verify=False)
    except Exception, e:
        print e
        return None

    if response.status_code == 200:
        try:
            data = response.json()
            if 'token' in data:
                token = data['token']
                # delete all the user credentials
                del(data, response, username, password)
            else:
                print "Authentication token not in response"

        except Exception, e:
            print e
            return None
    else:
        print "Authentication failed (%s: %s)" % (
            response.status_code, response.reason)

    return token


def get_projects(host, token, project_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROJECTS'])
    filter_params = dict()

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
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['PROJECTS'], project_pk)
    return get_request(token, url)


def get_specimens(host, token, specimen_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['SPECIMENS'])
    filter_params = dict()

    if specimen_name is not None:
        filter_params['specimen_name'] = specimen_name

    return get_request(token, url, filter_params)


def get_subject_groups(host, token, group_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SUBJECT_GROUPS'])
    filter_params = dict()

    if group_name is not None:
        filter_params['group_name'] = group_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_visit_types(host, token, visit_type_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['VISIT_TYPES'])
    filter_params = dict()

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
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['VISIT_TYPES'], visit_type_pk)
    return get_request(token, url)


def get_sites(host, token, site_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SITES'])
    filter_params = dict()

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
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['SITES'], site_pk)
    return get_request(token, url)


def get_subjects(host, token, subject_code=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SUBJECTS'])
    filter_params = dict()

    if subject_code is not None:
        filter_params['subject_code'] = subject_code

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
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['SUBJECTS'], subject_pk)
    return get_request(token, url)


def get_project_panels(host, token, panel_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROJECT_PANELS'])
    filter_params = dict()

    if panel_name is not None:
        filter_params['panel_name'] = panel_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_project_panel(host, token, project_panel_pk):
    """
    GET a serialized ProjectPanel instance
        project_panel_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['PROJECT_PANELS'], project_panel_pk)
    return get_request(token, url)


def get_site_panels(
        host, token, project_panel_pk=None, site_pk=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SITE_PANELS'])
    filter_params = dict()

    if site_pk is not None:
        filter_params['site'] = site_pk

    if project_panel_pk is not None:
        filter_params['project_panel'] = project_panel_pk

    if project_pk is not None:
        filter_params['site__project'] = project_pk

    return get_request(token, url, filter_params)


def get_site_panel(host, token, site_panel_pk):
    """
    GET a serialized ProjectPanel instance
        site_panel_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['SITE_PANELS'], site_panel_pk)
    return get_request(token, url)


def get_compensations(
        host,
        token,
        original_filename=None,
        site_pk=None,
        project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['COMPENSATIONS'])
    filter_params = dict()

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
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['COMPENSATIONS'], compensation_pk)
    return get_request(token, url)


def get_stimulations(host, token, project_pk=None, stimulation_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['STIMULATIONS'])
    filter_params = dict()

    if project_pk is not None:
        filter_params['project'] = project_pk

    if stimulation_name is not None:
        filter_params['stimulation_name'] = stimulation_name

    return get_request(token, url, filter_params)


def get_stimulation(host, token, stimulation_pk):
    """
    GET a serialized Stimulation instance
        stimulation_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['STIMULATIONS'], stimulation_pk)
    return get_request(token, url)


def get_samples(
        host,
        token,
        subject_pk=None,
        site_pk=None,
        project_pk=None,
        visit_pk=None,
        stimulation_pk=None,
        specimen_pk=None,
        site_panel_pk=None,
        project_panel_pk=None,
        original_filename=None,
        subject_code=None):
    url = '%s%s%s' % (METHOD, host, URLS['SAMPLES'])
    filter_params = dict()

    if subject_pk is not None:
        filter_params['subject'] = subject_pk

    if site_pk is not None:
        filter_params['site_panel__site'] = site_pk

    if project_pk is not None:
        filter_params['subject__project'] = project_pk

    if visit_pk is not None:
        filter_params['visit'] = visit_pk

    if stimulation_pk is not None:
        filter_params['stimulation'] = stimulation_pk

    if specimen_pk is not None:
        filter_params['specimen'] = specimen_pk

    if site_panel_pk is not None:
        filter_params['site_panel'] = site_panel_pk

    if project_panel_pk is not None:
        filter_params['site_panel__project_panel'] = project_panel_pk

    if original_filename is not None:
        filter_params['original_filename'] = original_filename

    if subject_code is not None:
        filter_params['subject__subject_code'] = subject_code

    return get_request(token, url, filter_params)


def get_sample(host, token, sample_pk):
    """
    GET a serialized Sample instance
        sample_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['SAMPLES'], sample_pk)
    return get_request(token, url)


def download_sample(
        host,
        token,
        sample_pk,
        data_format='npy',
        filename=None,
        directory=None):
    """
    Download sample data as FCS, CSV, or Numpy (npy)

    Options:
        'data_format': 'npy' (default), 'fcs, or 'csv'
        'filename': filename to use for downloaded file
                    (default is the PK.<format>, eg 42.npy)
    """
    if data_format == 'npy':
        url = "%s%s/api/repository/samples/%d/npy/" % (METHOD, host, sample_pk)
    elif data_format == 'csv':
        url = "%s%s/api/repository/samples/%d/csv/" % (METHOD, host, sample_pk)
    elif data_format == 'fcs':
        url = "%s%s/api/repository/samples/%d/fcs/" % (METHOD, host, sample_pk)
    else:
        print "Data format %s not supported, use 'npy', 'csv', or 'fcs'" \
            % data_format
        return

    if filename is None:
        filename = str(sample_pk) + '.' + data_format
    if directory is None:
        directory = os.getcwd()

    headers = {'Authorization': "Token %s" % token}
    data = ''
    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception, e:
        print e
        return {'status': None, 'reason': 'No response', 'data': data}

    if r.status_code == 200:
        try:
            with open("%s/%s" % (directory, filename), "wb") as data_file:
                data_file.write(r.content)
        except Exception, e:
            print e
    else:
        data = r.text

    return {
        'status': r.status_code,
        'reason': r.reason,
        'data': data,
    }


def download_samples(host, token, sample_pk_list, directory=None):
    urls = []

    for pk in sample_pk_list:
        urls.append(
            "%s%s/api/repository/samples/%d/fcs_as_pk/" %
            (METHOD, host, pk))
    headers = {'Authorization': "Token %s" % token}
    data = ''
    try:
        reqs = (grequests.get(u, headers=headers, verify=False) for u in urls)
        rs = grequests.map(reqs, size=5)
    except Exception, e:
        print e
        return {'status': None, 'reason': 'No response', 'data': data}

    results = []

    for r in rs:
        if r.status_code == 200:
            try:
                filename = re.findall(
                    "filename=([^']+)", r.headers['content-disposition'])[0]
                if directory is None:
                    directory = os.getcwd()

                with open("%s/%s" % (directory, filename), "wb") as fcs_file:
                    fcs_file.write(r.content)
            except Exception, e:
                print e
        else:
            data = r.text

        results.append({
            'status': r.status_code,
            'reason': r.reason,
            'data': data,
        })

    return results


def post_sample(
        host,
        token,
        file_path,
        subject_pk,
        visit_type_pk,
        specimen_pk,
        stimulation_pk,
        site_panel_pk,
        compensation_pk=None):
    """
    POST a FCS sample, associating the file with the following:
        subject_pk      (required)
        visit_type_pk   (required)
        specimen_pk     (required)
        stimulation_pk  (required)
        site_panel_pk   (required)
        compensation_pk (optional)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary string representation of object successfully posted,
                empty string if unsuccessful
    """

    url = '%s%s%s' % (METHOD, host, URLS['CREATE_SAMPLES'])
    headers = {'Authorization': "Token %s" % token}

    # Subject, visit, specimen, stimulation, and site_panel are required
    data = {
        'subject': subject_pk,
        'visit': visit_type_pk,
        'specimen': specimen_pk,
        'stimulation': stimulation_pk,
        'site_panel': site_panel_pk
    }

    # add the compensation field if present
    if compensation_pk:
        data['compensation'] = compensation_pk

    # get FCS file
    files = {
        'sample_file': open(file_path, "rb")
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            verify=False)
    except Exception, e:
        print e
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


#######################################
### START PROCESS MANAGER FUNCTIONS ###
###    Note: Most of these require  ###
###    the user to be a superuser   ###
###    or a Worker                  ###
#######################################
def get_processes(host, token, process_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROCESSES'])
    filter_params = dict()

    if process_name is not None:
        filter_params['process_name'] = process_name

    return get_request(token, url, filter_params)


def get_workers(host, token, worker_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['WORKERS'])
    filter_params = dict()

    if worker_name is not None:
        filter_params['worker_name'] = worker_name

    return get_request(token, url, filter_params)


def get_process_requests(
        host,
        token,
        process_pk=None,
        worker_pk=None,
        request_user_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROCESS_REQUESTS'])
    filter_params = dict()

    if process_pk is not None:
        filter_params['process'] = process_pk

    if worker_pk is not None:
        filter_params['worker'] = worker_pk

    if request_user_pk is not None:
        filter_params['request_user'] = request_user_pk

    return get_request(token, url, filter_params)


def get_viable_process_requests(
        host,
        token,
        process_pk=None,
        worker_pk=None,
        request_user_pk=None):
    """
    Returns process requests that are compatible with the requesting user
    i.e. the requesting user must be a Worker registered with the Process
    Also, only unassigned 'Pending' requests will be returned
    """
    url = '%s%s%s' % (METHOD, host, URLS['VIABLE_PROCESS_REQUESTS'])
    filter_params = dict()

    if process_pk is not None:
        filter_params['process'] = process_pk

    if worker_pk is not None:
        filter_params['worker'] = worker_pk

    if request_user_pk is not None:
        filter_params['request_user'] = request_user_pk

    return get_request(token, url, filter_params)


def get_process_request(host, token, process_request_pk):
    """
    GET a serialized ProcessRequest instance
        process_request_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object successfully GET'd,
                empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (
        METHOD,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk)
    return get_request(token, url)


def request_process_request_assignment(host, token, process_request_pk):
    """
    Requesting user must be a Worker registered with the Process and
    and the ProcessRequest must have 'Pending' status
    """
    url = '%s%s%s%s/%s' % (
        METHOD, host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'request_assignment')
    headers = {'Authorization': "Token %s" % token}

    try:
        r = requests.patch(
            url,
            data={
                'process_request':
                process_request_pk
            },
            headers=headers,
            verify=False)
    except Exception, e:
        print e
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


def verify_process_request_assignment(host, token, process_request_pk):
    """
    Result will include 'assignment': True of request.user (Worker) is assigned
    to the specified ProcessRequest
    """
    url = '%s%s%s%s/%s' % (
        METHOD,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'verify_assignment')
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def revoke_process_request_assignment(host, token, process_request_pk):
    """

    """
    url = '%s%s%s%s/%s' % (
        METHOD,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'revoke_assignment')
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def verify_worker(host, token):
    """
    Result will include 'worker': True if request.user is a Worker on host
    """
    url = '%s%s%s' % (METHOD, host, URLS['VERIFY_WORKER'])
    filter_params = dict()

    return get_request(token, url, filter_params)