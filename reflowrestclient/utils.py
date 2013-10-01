import requests
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
    'COMPENSATIONS': '/api/repository/compensations/',
    'PARAMETERS': '/api/repository/parameters/',
    'SAMPLE_GROUPS': '/api/repository/sample_groups/',
    'SAMPLES': '/api/repository/samples/',
    'UNCAT_SAMPLES': '/api/repository/samples/uncategorized/',
    'CREATE_SAMPLES': '/api/repository/samples/add/',
    'SAMPLE_SETS': '/api/repository/sample_sets/',
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
        print "Authentication failed (%s: %s)" % (response.status_code, response.reason)

    return token


def get_projects(host, token, project_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROJECTS'])
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
    url = '%s%s%s%s/' % (METHOD, host, URLS['PROJECTS'], project_pk)
    return get_request(token, url)


def get_specimens(host, token, specimen_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['SPECIMENS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if specimen_name is not None:
        filter_params['specimen_name'] = specimen_name

    return get_request(token, url, filter_params)


def get_subject_groups(host, token, group_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SUBJECT_GROUPS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if group_name is not None:
        filter_params['group_name'] = group_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_visit_types(host, token, visit_type_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['VISIT_TYPES'])
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
    url = '%s%s%s%s/' % (METHOD, host, URLS['VISIT_TYPES'], visit_type_pk)
    return get_request(token, url)


def get_sites(host, token, site_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SITES'])
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
    url = '%s%s%s%s/' % (METHOD, host, URLS['SITES'], site_pk)
    return get_request(token, url)


def get_subjects(host, token, subject_code=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SUBJECTS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

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
        'data': Dictionary representation of Subject object GET'd, empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['SUBJECTS'], subject_pk)
    return get_request(token, url)


def get_project_panels(host, token, panel_name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROJECT_PANELS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

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
        'data': Dictionary representation of Panel object GET'd, empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['PROJECT_PANELS'], project_panel_pk)
    return get_request(token, url)


def get_compensations(host, token, original_filename=None, site_pk=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['COMPENSATIONS'])
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
    url = '%s%s%s%s/' % (METHOD, host, URLS['COMPENSATIONS'], compensation_pk)
    return get_request(token, url)


def get_parameters(host, token, name=None, parameter_type=None, name_contains=None):
    url = '%s%s%s' % (METHOD, host, URLS['PARAMETERS'])
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
    url = '%s%s%s%s/' % (METHOD, host, URLS['PARAMETERS'], parameter_pk)
    return get_request(token, url)


def get_sample_groups(host, token, group_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['SAMPLE_GROUPS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if group_name is not None:
        filter_params['group_name'] = group_name

    return get_request(token, url, filter_params)


def get_samples(host, token, subject_pk=None, site_pk=None, project_pk=None, visit_pk=None, parameter_names=None, parameter_count=None):
    url = '%s%s%s' % (METHOD, host, URLS['SAMPLES'])
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

    if parameter_count is not None:
        filter_params['parameter_count'] = parameter_count

    return get_request(token, url, filter_params)


def get_uncat_samples(host, token, subject_pk=None, site_pk=None, project_pk=None, visit_pk=None, fcs_text=None, parameter_count=None):
    url = '%s%s%s' % (METHOD, host, URLS['UNCAT_SAMPLES'])
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

    if fcs_text is not None:
        filter_params['fcs_text'] = fcs_text

    if parameter_count is not None:
        filter_params['parameter_count'] = parameter_count

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
    url = '%s%s%s%s/' % (METHOD, host, URLS['SAMPLES'], sample_pk)
    return get_request(token, url)


def download_sample(host, token, sample_pk, filename=None, directory=None):
    url = "%s%s/api/repository/samples/%d/download/" % (METHOD, host, sample_pk)
    headers = {'Authorization': "Token %s" % token}
    data = ''
    try:
        r = requests.get(url, headers=headers, verify=False)
    except Exception, e:
        print e
        return {'status': None, 'reason': 'No response', 'data': data}

    if r.status_code == 200:
        try:
            if filename is None:
                filename = re.findall("filename=([^']+)", r.headers['content-disposition'])[0]
            if directory is None:
                directory = os.getcwd()

            with open("%s/%s" % (directory, filename), "wb") as fcs_file:
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


def post_sample(
    host,
    token,
    file_path,
    subject_pk,
    site_pk,
    visit_type_pk,
    specimen_pk,
    sample_group_pk=None,
    panel_pk=None):
    """
    POST a FCS sample, associating the file with the following:
        subject      (required)
        site         (required)
        visit_type   (required)
        specimen     (required)
        sample_group (optional)
        panel        (optional)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': JSON string representation of the Sample object successfully posted, empty string if unsuccessful
    """

    url = '%s%s%s' % (METHOD, host, URLS['CREATE_SAMPLES'])
    headers = {'Authorization': "Token %s" % token}

    # Subject, site, visit_type, and specimen are required
    data = {
        'subject': subject_pk,
        'site': site_pk,
        'visit': visit_type_pk,
        'specimen': specimen_pk,
    }

    # add the sample_group field if present
    if sample_group_pk:
        data['sample_group'] = sample_group_pk

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

    url = '%s%s/api/repository/samples/%s/apply_panel/' % (METHOD, host, sample_pk)
    headers = {'Authorization': "Token %s" % token}

    try:
        r = requests.patch(url, data={'panel': panel_pk}, headers=headers, verify=False)
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

    url = '%s%s/api/repository/samples/%s/add_compensation/' % (METHOD, host, sample_pk)
    headers = {'Authorization': "Token %s" % token}

    data = {
        'compensation': compensation_pk,
        'sample': sample_pk
    }

    try:
        r = requests.post(url, data=data, headers=headers, verify=False)
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


def get_sample_sets(host, token, name=None, project_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['SAMPLE_SETS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if name is not None:
        filter_params['name'] = name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_sample_set(host, token, sample_set_pk):
    """
    GET a serialized SampleSet instance
        sample_set_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object GET'd, empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['SAMPLE_SETS'], sample_set_pk)
    return get_request(token, url)


#######################################
### START PROCESS MANAGER FUNCTIONS ###
###    Note: Most of these require  ###
###    the user to be a superuser   ###
###    or a Worker                  ###
#######################################
def get_processes(host, token, process_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROCESSES'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if process_name is not None:
        filter_params['process_name'] = process_name

    return get_request(token, url, filter_params)


def get_workers(host, token, worker_name=None):
    url = '%s%s%s' % (METHOD, host, URLS['WORKERS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if worker_name is not None:
        filter_params['worker_name'] = worker_name

    return get_request(token, url, filter_params)


def get_process_requests(host, token, process_pk=None, worker_pk=None, request_user_pk=None):
    url = '%s%s%s' % (METHOD, host, URLS['PROCESS_REQUESTS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if process_pk is not None:
        filter_params['process'] = process_pk

    if worker_pk is not None:
        filter_params['worker'] = worker_pk

    if request_user_pk is not None:
        filter_params['request_user'] = request_user_pk

    return get_request(token, url, filter_params)


def get_viable_process_requests(host, token, process_pk=None, worker_pk=None, request_user_pk=None):
    """
    Returns process requests that are compatible with the requesting user
    i.e. the requesting user must be a Worker registered with the Process
    Also, only unassigned 'Pending' requests will be returned
    """
    url = '%s%s%s' % (METHOD, host, URLS['VIABLE_PROCESS_REQUESTS'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

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
        sample_set_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object GET'd, empty string if unsuccessful
    """
    url = '%s%s%s%s/' % (METHOD, host, URLS['PROCESS_REQUESTS'], process_request_pk)
    return get_request(token, url)


def request_process_request_assignment(host, token, process_request_pk):
    """
    Requesting user must be a Worker registered with the Process and
    and the ProcessRequest must have 'Pending' status
    """
    url = '%s%s%s%s/%s' % (METHOD, host, URLS['PROCESS_REQUESTS'], process_request_pk, 'request_assignment')
    headers = {'Authorization': "Token %s" % token}

    try:
        r = requests.patch(url, data={'process_request': process_request_pk}, headers=headers, verify=False)
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
    url = '%s%s%s%s/%s' % (METHOD, host, URLS['PROCESS_REQUESTS'], process_request_pk, 'verify_assignment')
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def revoke_process_request_assignment(host, token, process_request_pk):
    """

    """
    url = '%s%s%s%s/%s' % (METHOD, host, URLS['PROCESS_REQUESTS'], process_request_pk, 'revoke_assignment')
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def verify_worker(host, token):
    """
    Result will include 'worker': True if request.user is a Worker on host
    """
    url = '%s%s%s' % (METHOD, host, URLS['VERIFY_WORKER'])
    filter_params = dict()
    filter_params['paginate_by'] = '0'

    return get_request(token, url, filter_params)