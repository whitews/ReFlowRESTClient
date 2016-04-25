import requests
import os
import json

METHOD = {
    'https': 'https://',
    'http': 'http://'
}

URLS = {
    'TOKEN':               '/api/token-auth/',
    'PROJECTS':            '/api/repository/projects/',
    'SPECIMENS':           '/api/repository/specimens/',
    'SUBJECT_GROUPS':      '/api/repository/subject_groups/',
    'SITES':               '/api/repository/sites/',
    'SUBJECTS':            '/api/repository/subjects/',
    'PROJECT_PANELS':      '/api/repository/panel_templates/',
    'SITE_PANELS':         '/api/repository/site_panels/',
    'COMPENSATIONS':       '/api/repository/compensations/',
    'CREATE_COMPENSATION': '/api/repository/compensations/add/',
    'STIMULATIONS':        '/api/repository/stimulations/',
    'SAMPLES':             '/api/repository/samples/',
    'CREATE_SAMPLES':      '/api/repository/samples/add/',
    'SAMPLE_METADATA':     '/api/repository/samplemetadata/',
    'VISIT_TYPES':         '/api/repository/visit_types/',
    'SAMPLE_COLLECTION':   '/api/repository/sample_collections/',

    # Process related API URLs
    'PROCESSES':                 '/api/repository/processes/',
    'WORKERS':                   '/api/repository/workers/',
    'VERIFY_WORKER':             '/api/repository/verify_worker/',
    'PROCESS_REQUESTS':          '/api/repository/process_requests/',
    'VIABLE_PROCESS_REQUESTS':   '/api/repository/viable_process_requests/',
    'ASSIGNED_PROCESS_REQUESTS': '/api/repository/assigned_process_requests/',
    'CLUSTERS':                  '/api/repository/clusters/',
    'SAMPLE_CLUSTERS':           '/api/repository/sample_clusters/',
    'SAMPLE_CLUSTER_COMPONENTS': '/api/repository/sample_cluster_components/',
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

    response = requests.get(url, headers=headers, params=params, verify=False)

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


def get_token(host, username, password, method=METHOD['https']):
    """
    Login to host url using user credentials given.

    Returns the authenticating user's token (string) if successful,
    returns None if authentication failed.
    """
    url = '%s%s%s' % (method, host, URLS['TOKEN'])

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


def get_projects(host, token, project_name=None, method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['PROJECTS'])
    filter_params = dict()

    if project_name is not None:
        filter_params['project_name'] = project_name

    return get_request(token, url, filter_params)


def get_project(host, token, project_pk, method=METHOD['https']):
    """
    GET a serialized Project instance
        project_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['PROJECTS'], project_pk)
    return get_request(token, url)


def get_specimens(host, token, specimen_name=None, method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SPECIMENS'])
    filter_params = dict()

    if specimen_name is not None:
        filter_params['specimen_name'] = specimen_name

    return get_request(token, url, filter_params)


def get_subject_groups(
        host,
        token,
        group_name=None,
        project_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SUBJECT_GROUPS'])
    filter_params = dict()

    if group_name is not None:
        filter_params['group_name'] = group_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_visit_types(
        host,
        token,
        visit_type_name=None,
        project_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['VISIT_TYPES'])
    filter_params = dict()

    if visit_type_name is not None:
        filter_params['visit_type_name'] = visit_type_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_visit_type(host, token, visit_type_pk, method=METHOD['https']):
    """
    GET a serialized ProjectVisitType instance
        visit_type_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['VISIT_TYPES'], visit_type_pk)
    return get_request(token, url)


def get_sites(
        host,
        token,
        site_name=None,
        project_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SITES'])
    filter_params = dict()

    if site_name is not None:
        filter_params['site_name'] = site_name

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_site(host, token, site_pk, method=METHOD['https']):
    """
    GET a serialized Site instance
        site_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['SITES'], site_pk)
    return get_request(token, url)


def get_subjects(
        host,
        token,
        subject_code=None,
        project_pk=None,
        subject_group_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SUBJECTS'])
    filter_params = dict()

    if subject_code is not None:
        filter_params['subject_code'] = subject_code

    if project_pk is not None:
        filter_params['project'] = project_pk

    if subject_group_pk is not None:
        filter_params['subject_group'] = subject_group_pk

    return get_request(token, url, filter_params)


def get_subject(host, token, subject_pk, method=METHOD['https']):
    """
    GET a serialized Subject instance
        subject_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['SUBJECTS'], subject_pk)
    return get_request(token, url)


def get_project_panels(
        host,
        token,
        panel_name=None,
        staining=None,
        project_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['PROJECT_PANELS'])
    filter_params = dict()

    if panel_name is not None:
        filter_params['panel_name'] = panel_name

    if staining is not None:
        filter_params['staining'] = staining

    if project_pk is not None:
        filter_params['project'] = project_pk

    return get_request(token, url, filter_params)


def get_project_panel(host, token, project_panel_pk, method=METHOD['https']):
    """
    GET a serialized ProjectPanel instance
        project_panel_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['PROJECT_PANELS'], project_panel_pk)
    return get_request(token, url)


def get_site_panels(
        host,
        token,
        project_panel_pk=None,
        site_pk=None,
        project_pk=None,
        panel_type=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SITE_PANELS'])
    filter_params = dict()

    if site_pk is not None:
        filter_params['site'] = site_pk

    if project_panel_pk is not None:
        filter_params['panel_template'] = project_panel_pk

    if project_pk is not None:
        filter_params['project'] = project_pk

    if panel_type is not None:
        filter_params['panel_type'] = panel_type

    return get_request(token, url, filter_params)


def get_site_panel(host, token, site_panel_pk, method=METHOD['https']):
    """
    GET a serialized SitePanel instance
        site_panel_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['SITE_PANELS'], site_panel_pk)
    return get_request(token, url)


def is_site_panel_match(
        host,
        token,
        site_panel_pk,
        parameter_dict,
        method=METHOD['https']):
    """
    GET a serialized ProjectPanel instance
        site_panel_pk    (required)

    Returns True/False whether dictionary matches the site panel
    """

    # TODO: verify the parameter_dict

    response = get_site_panel(host, token, site_panel_pk, method=method)

    site_parameters = None

    if 'data' in response:
        if 'parameters' in response['data']:
            site_parameters = response['data']['parameters']

    matches = dict()
    non_matches = dict()
    missing = dict()

    if site_parameters:
        for param in site_parameters:
            if 'fcs_number' in param:
                if param['fcs_number'] in parameter_dict:
                    candidate = parameter_dict[param['fcs_number']]
                    if 'n' not in candidate:
                        non_matches[param['fcs_number']] = candidate
                        continue
                    if candidate['n'] != param['fcs_text']:
                        non_matches[param['fcs_number']] = candidate
                        continue
                    if 's' not in candidate and param['fcs_opt_text'] != '':
                        non_matches[param['fcs_number']] = candidate
                        continue
                    elif 's' in candidate:
                        if candidate['s'] != param['fcs_opt_text']:
                            non_matches[param['fcs_number']] = candidate
                            continue
                    # if we get here, everything matched
                    matches[param['fcs_number']] = candidate
                else:
                    missing[param['fcs_number']] = [
                        param['fcs_text'],
                        param['fcs_opt_text']
                    ]

    if (len(matches) == len(site_parameters)) and \
            len(non_matches) == 0 and \
            len(missing) == 0:
        return True

    return False


def get_compensations(
        host,
        token,
        name=None,
        site_panel_pk=None,
        site_pk=None,
        project_pk=None,
        acquisition_date=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['COMPENSATIONS'])
    filter_params = dict()

    if name is not None:
        filter_params['name'] = name

    if site_panel_pk is not None:
        filter_params['site_panel'] = site_panel_pk

    if site_pk is not None:
        filter_params['site'] = site_pk

    if project_pk is not None:
        filter_params['project'] = project_pk

    if acquisition_date is not None:
        filter_params['acquisition_date'] = acquisition_date

    return get_request(token, url, filter_params)


def get_compensation(host, token, compensation_pk, method=METHOD['https']):
    """
    GET a serialized Compensation instance
        compensation_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['COMPENSATIONS'], compensation_pk)
    return get_request(token, url)


def get_stimulations(
        host,
        token,
        project_pk=None,
        stimulation_name=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['STIMULATIONS'])
    filter_params = dict()

    if project_pk is not None:
        filter_params['project'] = project_pk

    if stimulation_name is not None:
        filter_params['stimulation_name'] = stimulation_name

    return get_request(token, url, filter_params)


def get_stimulation(host, token, stimulation_pk, method=METHOD['https']):
    """
    GET a serialized Stimulation instance
        stimulation_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['STIMULATIONS'], stimulation_pk)
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
        subject_code=None,
        acquisition_date=None,
        sha1=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SAMPLES'])
    filter_params = dict()

    if subject_pk is not None:
        filter_params['subject'] = subject_pk

    if site_pk is not None:
        filter_params['site'] = site_pk

    if project_pk is not None:
        filter_params['project'] = project_pk

    if visit_pk is not None:
        filter_params['visit'] = visit_pk

    if stimulation_pk is not None:
        filter_params['stimulation'] = stimulation_pk

    if specimen_pk is not None:
        filter_params['specimen'] = specimen_pk

    if site_panel_pk is not None:
        filter_params['site_panel'] = site_panel_pk

    if project_panel_pk is not None:
        filter_params['panel'] = project_panel_pk

    if original_filename is not None:
        filter_params['original_filename'] = original_filename

    if subject_code is not None:
        filter_params['subject_code'] = subject_code

    if acquisition_date is not None:
        filter_params['acquisition_date'] = acquisition_date

    if sha1 is not None:
        filter_params['sha1'] = sha1

    return get_request(token, url, filter_params)


def get_sample(host, token, sample_pk, method=METHOD['https']):
    """
    GET a serialized Sample instance
        sample_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (method, host, URLS['SAMPLES'], sample_pk)
    return get_request(token, url)


def download_sample(
        host,
        token,
        sample_pk,
        filename=None,
        directory=None,
        method=METHOD['https']):
    """
    Download sample as FCS
    """
    url = "%s%s/api/repository/samples/%d/fcs/" % (method, host, sample_pk)

    if filename is None:
        filename = str(sample_pk) + '.fcs'
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


def post_sample(
        host,
        token,
        file_path,
        subject_pk,
        visit_type_pk,
        specimen_pk,
        pretreatment,
        storage,
        stimulation_pk,
        site_panel_pk,
        acquisition_date,
        compensation_pk=None,
        method=METHOD['https']):
    """
    POST a FCS sample, associating the file with the following:
        subject_pk       (required)
        visit_type_pk    (required)
        specimen_pk      (required)
        pretreatment     (required)
        storage          (required)
        stimulation_pk   (required)
        site_panel_pk    (required)
        acquisition_date (required)
        compensation_pk  (optional)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary string representation of object successfully posted,
                empty string if unsuccessful
    """

    url = '%s%s%s' % (method, host, URLS['CREATE_SAMPLES'])
    headers = {'Authorization': "Token %s" % token}

    # Subject, visit, specimen, stimulation, and site_panel are required
    data = {
        'subject': subject_pk,
        'visit': visit_type_pk,
        'specimen': specimen_pk,
        'pretreatment': pretreatment,
        'storage': storage,
        'stimulation': stimulation_pk,
        'site_panel': site_panel_pk,
        'acquisition_date': acquisition_date
    }

    # add the compensation field if present
    if compensation_pk:
        data['compensation'] = compensation_pk

    file_obj = open(file_path, "rb")

    # get FCS file
    files = {
        'sample_file': (os.path.basename(file_obj.name), file_obj)
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            verify=False)
    except Exception, e:
        file_obj.close()
        print e
        return {'status': None, 'reason': 'No response', 'data': ''}

    file_obj.close()

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


def get_sample_metadata(
        host,
        token,
        sample_pk=None,
        key=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SAMPLE_METADATA'])
    filter_params = dict()

    if sample_pk is not None:
        filter_params['sample'] = sample_pk

    if key is not None:
        filter_params['key'] = key

    return get_request(token, url, filter_params)


def get_sample_collection(
        host,
        token,
        sample_collection_pk,
        method=METHOD['https']):
    """
    GET a serialized Sample Collection instance
        sample_collection_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (
        method,
        host,
        URLS['SAMPLE_COLLECTION'],
        sample_collection_pk
    )
    return get_request(token, url)


def download_compensation(
        host,
        token,
        compensation_pk,
        data_format='npy',
        filename=None,
        directory=None,
        method=METHOD['https']):
    """
    Download sample data as CSV or Numpy (npy)

    Options:
        'data_format': 'npy' (default) or 'csv'
        'filename': filename to use for downloaded file
                    (default is the comp_<PK>.<format>, eg comp_42.npy)
    """
    if data_format == 'npy':
        url = "%s%s/api/repository/compensations/%d/npy/" % (
            method, host, compensation_pk)
    elif data_format == 'csv':
        url = "%s%s/api/repository/compensations/%d/csv/" % (
            method, host, compensation_pk)
    else:
        print "Data format %s not supported, use 'npy' or 'csv'" \
            % data_format
        return

    if filename is None:
        filename = 'comp_' + str(compensation_pk) + '.' + data_format
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


def post_compensation(
        host,
        token,
        name,
        panel_template_pk,
        acquisition_date,
        matrix_text,
        method=METHOD['https']):
    """
    POST a compensation matrix. The matrix text can be comma or tab delimited.
        name              (required)
        panel_template_pk (required)
        acquisition_date  (required)
        matrix_text       (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary string representation of object successfully posted,
                empty string if unsuccessful
    """

    url = '%s%s%s' % (method, host, URLS['CREATE_COMPENSATION'])
    headers = {'Authorization': "Token %s" % token}

    # Subject, visit, specimen, stimulation, and site_panel are required
    data = {
        'name': name,
        'panel_template': panel_template_pk,
        'acquisition_date': acquisition_date,
        'matrix_text': matrix_text
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
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


###################################
# START PROCESS MANAGER FUNCTIONS #
#    Note: Most of these require  #
#    the user to be a superuser   #
#    or a Worker                  #
###################################
def get_processes(host, token, process_name=None, method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['PROCESSES'])
    filter_params = dict()

    if process_name is not None:
        filter_params['process_name'] = process_name

    return get_request(token, url, filter_params)


def get_workers(host, token, worker_name=None, method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['WORKERS'])
    filter_params = dict()

    if worker_name is not None:
        filter_params['worker_name'] = worker_name

    return get_request(token, url, filter_params)


def get_process_requests(
        host,
        token,
        process_pk=None,
        worker_pk=None,
        request_user_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['PROCESS_REQUESTS'])
    filter_params = dict()

    if process_pk is not None:
        filter_params['process'] = process_pk

    if worker_pk is not None:
        filter_params['worker'] = worker_pk

    if request_user_pk is not None:
        filter_params['request_user'] = request_user_pk

    return get_request(token, url, filter_params)


def get_assigned_process_requests(
        host,
        token,
        method=METHOD['https']):
    """
    Returns process requests that are assigned to the requesting worker
    i.e. the requesting user must be a Worker in the ReFlow server
    Also, only non-Completed requests will be returned
    """
    url = '%s%s%s' % (method, host, URLS['ASSIGNED_PROCESS_REQUESTS'])
    filter_params = dict()

    return get_request(token, url, filter_params)


def get_viable_process_requests(
        host,
        token,
        process_pk=None,
        worker_pk=None,
        request_user_pk=None,
        method=METHOD['https']):
    """
    Returns process requests that are compatible with the requesting user
    i.e. the requesting user must be a Worker registered with the Process
    Also, only unassigned 'Pending' requests will be returned
    """
    url = '%s%s%s' % (method, host, URLS['VIABLE_PROCESS_REQUESTS'])
    filter_params = dict()

    if process_pk is not None:
        filter_params['process'] = process_pk

    if worker_pk is not None:
        filter_params['worker'] = worker_pk

    if request_user_pk is not None:
        filter_params['request_user'] = request_user_pk

    return get_request(token, url, filter_params)


def get_process_request(
        host,
        token,
        process_request_pk,
        method=METHOD['https']):
    """
    GET a serialized ProcessRequest instance
        process_request_pk    (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary representation of object
    """
    url = '%s%s%s%s/' % (
        method,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk)
    return get_request(token, url)


def request_pr_assignment(
        host,
        token,
        process_request_pk,
        method=METHOD['https']):
    """
    Requesting user must be a Worker registered with the Process and
    and the ProcessRequest must have 'Pending' status
    """
    url = '%s%s%s%s/%s/' % (
        method,
        host,
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


def report_pr_error(
        host,
        token,
        process_request_pk,
        error_msg_string,
        method=METHOD['https']):
    """
    Requesting user must be a Worker assigned to the ProcessRequest and
    and the ProcessRequest must have 'Worker' status
    """
    url = '%s%s%s%s/%s/' % (
        method,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'report_error')
    headers = {'Authorization': "Token %s" % token}

    r = requests.patch(
        url,
        data={
            'status_message': error_msg_string
        },
        headers=headers,
        verify=False
    )

    if r.status_code == 201:
        data = r.json()
    else:
        data = r.text

    return {
        'status': r.status_code,
        'reason': r.reason,
        'data': data,
    }


def verify_pr_assignment(
        host,
        token,
        process_request_pk,
        method=METHOD['https']):
    """
    Result will include 'assignment': True of request.user (Worker) is assigned
    to the specified ProcessRequest
    """
    url = '%s%s%s%s/%s/' % (
        method,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'verify_assignment')
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def revoke_pr_assignment(
        host,
        token,
        process_request_pk,
        method=METHOD['https']):
    """
    Requests un-assignment from a ProcessRequest on the ReFlow server
    """
    url = '%s%s%s%s/%s/' % (
        method,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'revoke_assignment')
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def purge_pr_results(
        host,
        token,
        process_request_pk,
        method=METHOD['https']):
    """
    Requests that previous ProcessRequest results be deleted. Only works
    for uncompleted PRs, and only for the assigned Worker.
    """
    url = '%s%s%s%s/%s/' % (
        method,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'purge_results')
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def report_pr_progress(
        host,
        token,
        process_request_pk,
        percent_complete,
        method=METHOD['https']):
    """
    Requesting user must be a Worker assigned to the ProcessRequest and
    and the ProcessRequest must have 'Worker' status. Percent complete should
    be an integer, and will be reported back as such to the ReFlow server.
    """
    url = '%s%s%s%s' % (
        method,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk)
    headers = {'Authorization': "Token %s" % token}

    r = requests.patch(
        url,
        data={
            'percent_complete': percent_complete
        },
        headers=headers,
        verify=False
    )

    if r.status_code == 201:
        data = r.json()
    else:
        data = r.text

    return {
        'status': r.status_code,
        'reason': r.reason,
        'data': data,
    }


def complete_pr_assignment(
        host,
        token,
        process_request_pk,
        method=METHOD['https']):
    """
    Report that the ProcessRequest has been completed
    """
    url = '%s%s%s%s/%s/' % (
        method,
        host,
        URLS['PROCESS_REQUESTS'],
        process_request_pk,
        'complete_assignment')
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def verify_worker(host, token, method=METHOD['https']):
    """
    Result will include 'worker': True if request.user is a Worker on host
    """
    url = '%s%s%s' % (method, host, URLS['VERIFY_WORKER'])
    filter_params = dict()

    return get_request(token, url, filter_params)


def post_cluster(
        host,
        token,
        process_request_id,
        cluster_index,
        method=METHOD['https']):
    """
    POST a Cluster instance.
        process_request_id (required)
        cluster_index      (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary string representation of object successfully posted,
                empty string if unsuccessful
    """

    url = '%s%s%s' % (method, host, URLS['CLUSTERS'])
    headers = {'Authorization': "Token %s" % token}

    # process_request and index are required
    data = {
        'process_request': process_request_id,
        'index': cluster_index
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
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


def post_sample_cluster(
        host,
        token,
        cluster_id,
        sample_id,
        param_dict,
        events,
        components,
        method=METHOD['https']):
    """
    POST a SampleCluster instance.
        cluster_id     (required)
        param_dict     (required)
        event_indices  (required)

    Returns a dictionary with keys:
        'status': The HTTP response code
        'reason': The HTTP response reason
        'data': Dictionary string representation of object successfully posted,
                empty string if unsuccessful
    """

    url = '%s%s%s' % (method, host, URLS['SAMPLE_CLUSTERS'])
    headers = {
        'Authorization': "Token %s" % token,
        'Content-type': 'application/json'  # b/c of the nested param_dict
    }

    # process_request and index are required
    data = {
        'cluster_id': cluster_id,
        'sample_id': sample_id,
        'parameters': param_dict,
        'events': events,
        'components': components
    }

    # convert to JSON b/c of nested objects (param_dict)
    data = json.dumps(data)

    response = requests.post(
        url,
        headers=headers,
        data=data,
        verify=False)

    if response.status_code == 201:
        try:
            data = response.json()
        except Exception, e:
            # Since we got a 201 response but couldn't JSON-ify the response,
            # we still need to return something sensible
            data = response.text()
            print e
    else:
        data = response.text

    return {
        'status': response.status_code,
        'reason': response.reason,
        'data': data,
    }


def get_sample_clusters(
        host,
        token,
        process_request_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SAMPLE_CLUSTERS'])
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk

    return get_request(token, url, filter_params)


def get_sample_cluster_components(
        host,
        token,
        process_request_pk=None,
        sample_pk=None,
        method=METHOD['https']):
    url = '%s%s%s' % (method, host, URLS['SAMPLE_CLUSTER_COMPONENTS'])
    filter_params = dict()

    if process_request_pk is not None:
        filter_params['process_request'] = process_request_pk
    if sample_pk is not None:
        filter_params['sample'] = sample_pk

    return get_request(token, url, filter_params)


def download_sample_cluster_events(
        host,
        token,
        sample_cluster_pk,
        filename=None,
        directory=None,
        method=METHOD['https']):
    """
    Download sample data as CSV or Numpy (npy)

    Options:
        'data_format': 'npy' (default) or 'csv'
        'filename': filename to use for downloaded file
                    (default is the comp_<PK>.<format>, eg comp_42.npy)
    """
    url = "%s%s/api/repository/sample_clusters/%d/csv/" % (
        method,
        host,
        sample_cluster_pk
    )

    if filename is None:
        filename = 'sample_cluster_' + str(sample_cluster_pk) + '.csv'
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
