import requests
import re
import xml.etree.ElementTree as ET
import urllib3


# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


### modified from https://github.com/tableau/rest-api-samples/blob/master/python/update_permission.py
#### each function/method uses the following steps:
##       1. Create url variable (can be found in API docs)
##       2. Build XMl request elements and subelements using Element tree (if applicable). XML request specifications can be found in API documentation
##       3. converts Elementtree to string
##       4. sends request using python requests library
##       5. checks server response for error 
##       6. converts server response to string, parses response to return relevant values (if applicable)


class ApiCallError(Exception):
    pass


class UserDefinedFieldError(Exception):
    pass


def _encode_for_display(text):
    """
    Encodes strings so they can display as ASCII in a Windows terminal window.
    This function also encodes strings for processing by xml.etree.ElementTree functions.
    Returns an ASCII-encoded version of the text.
    Unicode characters are converted to ASCII placeholders (for example, "?").
    """
    return text.encode('ascii', errors = "backslashreplace").decode('utf-8')


def _check_status(server_response, success_code, xmlns):
    """
    Checks the server response for possible errors.
    'server_response'       the response received from the server
    'success_code'          the expected success code for the response
    Throws an ApiCallError exception if the API call fails.
    """
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)

        # Obtain the 3 xml tags from the response: error, summary, and detail tags
        error_element = parsed_response.find('t:error', namespaces = xmlns)
        summary_element = parsed_response.find('.//t:summary', namespaces = xmlns)
        detail_element = parsed_response.find('.//t:detail', namespaces = xmlns)

        # Retrieve the error code, summary, and detail if the response contains them
        code = error_element.get('code', 'unknown') if error_element is not None else 'unknown code'
        summary = summary_element.text if summary_element is not None else 'unknown summary'
        detail = detail_element.text if detail_element is not None else 'unknown detail'
        error_message = '{0}: {1} - {2}'.format(code, summary, detail)
        raise ApiCallError(error_message)
    return

def _check_user_input(input, list):
    """
    input: a group or user uuid from the tableau server
    list: a list of group uuids/ user uuids on the tableau server
    used as a check to display a more helpful error if the uuid is not found on the tableua server
    """
    if input not in list:
        raise ValueError("{0} not found".format(input))
    return

def sign_in(server, username, password, VERSION, xmlns, site=""):
    """
    server: e.g http://tableau.mycompany.com
    username: your tableau username
    password: your tableau password
    site: use if you have multiple sites - default is empty string
    #references https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm
    These variables can be set in the settings.py file (as global variables); the option to include
    them separately in the functions is preserved so you can use tableau_rest.py base functions as stand-alone code
    or as part of the larger tabula module
    VERSION is the tableau REST API server (e.g '3.11')
    xmlns = the namespaces for the API request e.g {'t': 'http://tableau.com/api'}
    returns token, site_id and user_id in that order to be saved using those specific variable names for future API calls
    """
    url = server + "/api/{0}/auth/signin".format(VERSION)
    # Builds the request as xml_object
    xml_request = ET.Element('tsRequest')
    credentials_element = ET.SubElement(xml_request, 'credentials', name=username, password=password)
    ET.SubElement(credentials_element, 'site', contentUrl=site)
    xml_request = ET.tostring(xml_request)
    # Make the request to server
    server_response = requests.post(url, data=xml_request, verify=False) ###add timeout=15
    _check_status(server_response, 200, xmlns)
    # # ASCII encode server response to enable displaying to console
    server_response = _encode_for_display(server_response.text)
    ## without _check_status function:
    # server_response=server_response.text.encode('ascii', errors="backslashreplace").decode('utf-8')
    # Reads and parses the response
    parsed_response = ET.fromstring(server_response)
    # Gets the auth token and site ID
    token = parsed_response.find('t:credentials', namespaces = xmlns).get('token')
    site_id = parsed_response.find('.//t:site', namespaces = xmlns).get('id')
    user_id = parsed_response.find('.//t:user', namespaces = xmlns).get('id')
    return token, site_id, user_id

def sign_out(server, VERSION, xmlns):
    ### POST /api/api-version/auth/signout
    url = server + "/api/{0}/auth/signout".format(VERSION)
    server_response = requests.post(url, verify=False)
    _check_status(server_response, 204, xmlns)

class QueryProjects():
    """
    performs single API call that returns xml data for projects. xml is parsed using associated methods
    """
    def __init__(self, VERSION, site_id, token, server, xmlns):
        self.VERSION = VERSION
        self.site_id = site_id
        url = server + "/api/{0}/sites/{1}/projects".format(VERSION, site_id)
        # xml_request = 'none'
        server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
        _check_status(server_response, 200, xmlns)
        server_response = _encode_for_display(server_response.text)
        parsed_response = ET.fromstring(server_response)
        self.projects = parsed_response.findall('.//t:project', namespaces=xmlns)
        self.project_names= [proj.get('name') for proj in self.projects]
        self.project_ids= [proj.get('id') for proj in self.projects]

    def project_id_from_name(self, project_name):
        _check_user_input(project_name, self.project_names)
        if project_name in self.project_names:
            project_id = [project.get('id') for project in self.projects if project.get('name') == project_name]
            return project_id[0]
        
    def project_name_from_id(self, project_id):
        _check_user_input(project_id, self.project_ids)
        if project_id in self.project_ids:
            project_name = [project.get('name') for project in self.projects if project.get('id') == project_id]
            return project_name[0]
    
    def project_description_from_name(self, project_name):
        _check_user_input(project_name, self.project_names)
        if project_name in self.project_names:
            project_description = [project.get('description') for project in self.projects if project.get('name') == project_name]
            return project_description[0]
        
    def project_controllingpermissions_from_name(self, project_name):
        _check_user_input(project_name, self.project_names)
        if project_name in self.project_names:
            project_controllingpermissions_id = [project.get('controllingPermissionsProjectId') for project in self.projects if project.get('name') == project_name]
            return project_controllingpermissions_id[0]
    
    def project_createdat_from_name(self, project_name):
        _check_user_input(project_name, self.project_names)
        if project_name in self.project_names:
            project_createdat = [project.get('createdAt') for project in self.projects if project.get('name') == project_name]
            return project_createdat[0]
    
    def project_updatedat_from_name(self, project_name):
        _check_user_input(project_name, self.project_names)
        if project_name in self.project_names:
            project_updatedat = [project.get('updatedAt') for project in self.projects if project.get('name') == project_name]
            return project_updatedat[0]
    
    def project_permissionslocked_from_name(self, project_name):
        _check_user_input(project_name, self.project_names)
        if project_name in self.project_names:
            project_contentpermissions = [project.get('contentPermissions') for project in self.projects if project.get('name') == project_name]
            return project_contentpermissions[0]

class QueryWorkbooks():
    """
    performs single API call that returns xml data for workbooks. xml is parsed using associated methods
    """
    def __init__(self, VERSION, site_id, token, server, xmlns):
        self.VERSION = VERSION
        self.site_id = site_id
        self.server = server
        self.xmlns = xmlns
        # GET /api/api-version/sites/site-id/workbooks
        url = server + "/api/{0}/sites/{1}/workbooks?pageSize=300".format(VERSION, site_id)
        # xml_request = 'none'
        server_response = requests.get(url, headers={'x-tableau-auth': token}, verify = False)
        _check_status(server_response, 200, xmlns)
        server_response = _encode_for_display(server_response.text)
        parsed_response = ET.fromstring(server_response)
        self.workbooks = parsed_response.findall('.//t:workbook', namespaces = xmlns)
        self.workbook_names= [workbook.get('name') for workbook in self.workbooks]
        self.workbook_ids= [workbook.get('id') for workbook in self.workbooks]

    def workbook_id_from_name(self, workbook_name):
        _check_user_input(workbook_name, self.workbook_names)
        if workbook_name in self.workbook_names:
            workbook_id = [workbook.get('id') for workbook in self.workbooks if workbook.get('name') == workbook_name]
        return workbook_id[0]

    def workbook_name_from_id(self, workbook_id):
        _check_user_input(workbook_id, self.workbook_ids)
        if workbook_id in self.workbook_ids:
            workbook_name = [workbook.get('name') for workbook in self.workbooks if workbook.get('id') == workbook_id]
        return workbook_name[0]
    
    def workbooks_from_projectid(self, project_id, xmlns):
        workbook_names = [workbook.get('name') for workbook in self.workbooks if workbook.find('.//t:project', namespaces = xmlns).get('id') == project_id]
        return workbook_names

def download_workbook(VERSION, site_id, token, xmlns, workbook_id, server, include_extract = False):
    #GET /api/api-version/sites/site-id/workbooks/workbook-id/content
    # GET /api/api-version/sites/site-id/workbooks/workbook-id/content?includeExtract=extract-value
    url = server + "/api/{0}/sites/{1}/workbooks/{2}/content?includeExtract={3}".format(VERSION, site_id, workbook_id, include_extract)
    # xml_request = 'none'
    server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    # Header format: Content-Disposition: name="tableau_workbook"; filename="workbook-filename"
    filename = re.findall(r'filename="(.*)"', server_response.headers['Content-Disposition'])[0]
    with open(filename, 'wb') as f:
        f.write(server_response.content)
    return filename


class QueryWorkbookViews():
    """
    performs single API call that returns xml data for workbooks. xml is parsed using associated methods
    """
    def __init__(self, VERSION, site_id, token, xmlns, workbook_id, server):
        self.VERSION = VERSION
        self.site_id = site_id
        self.server = server
        # GET /api/api-version/sites/site-id/workbooks/workbook-id/views
        url = server + "/api/{0}/sites/{1}/workbooks/{2}/views".format(VERSION, site_id, workbook_id)
        server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
        _check_status(server_response, 200, xmlns)
        server_response = _encode_for_display(server_response.text)
        parsed_response = ET.fromstring(server_response)
        self.views = parsed_response.findall('.//t:view', namespaces=xmlns)
        self.view_names= [view.get('name') for view in self.views]
        self.view_ids= [view.get('id') for view in self.views]

    def view_id_from_name(self, view_name):
        _check_user_input(view_name, self.view_names)
        if view_name in self.view_names:
            view_id = [view.get('id') for view in self.views if view.get('name') == view_name]
        return view_id[0]

    def view_name_from_id(self, view_id):
        _check_user_input(view_id, self.view_ids)
        if view_id in self.view_ids:
            view_name = [view.get('name') for view in self.views if view.get('id') == view_id]
        return view_name[0]

    def view_contenturl_from_id(self, view_id):
        _check_user_input(view_id, self.view_ids)
        if view_id in self.view_ids:
            view_contenturl = [view.get('contentUrl') for view in self.views if view.get('id') == view_id]
        return view_contenturl[0]

def query_view_data(VERSION, site_id, token, xmlns, view_id, server):
    # GET /api/api-version/sites/site-id/views/view-id/data
    url = server + "/api/{0}/sites/{1}/views/{2}/data".format(VERSION, site_id, view_id)
    # xml_request = 'none'
    server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    server_response = _encode_for_display(server_response.text)
    # parsed_response = ET.fromstring(server_response)
    return server_response

class QueryGroups():
    """
    performs single API call that returns xml data for groups. xml is parsed using associated methods
    """
    def __init__(self, VERSION, site_id, token, server, xmlns):
        self.VERSION = VERSION
        self.site_id = site_id
        self.server = server
        self.xmlns = xmlns
        # GET /api/api-version/sites/site-id/groups/
        url = server + "/api/{0}/sites/{1}/groups".format(VERSION, site_id)
        # xml_request = 'none'
        server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
        _check_status(server_response, 200, xmlns)
        server_response = _encode_for_display(server_response.text)
        parsed_response = ET.fromstring(server_response)
        self.groups = parsed_response.findall('.//t:group', namespaces=xmlns)

        self.group_names= [group.get('name') for group in self.groups]
        self.group_ids= [group.get('id') for group in self.groups]

    def group_id_from_name(self, group_name):
        _check_user_input(group_name, self.group_names)
        if group_name in self.group_names:
            group_id = [group.get('id') for group in self.groups if group.get('name') == group_name]
        return group_id[0]

    def group_name_from_id(self, group_id):
        _check_user_input(group_id, self.group_ids)
        if group_id in self.group_ids:
            group_name = [group.get('name') for group in self.groups if group.get('id') == group_id]
        return group_name[0]


class QueryUsers():
    """
    performs single API call that returns xml data for users. xml is parsed using associated methods
    """
    def __init__(self, VERSION, site_id, token, server, xmlns):
        self.VERSION = VERSION
        self.site_id = site_id
        self.server = server
        self.xmlns = xmlns
        # GET /api/api-version/sites/site-id/users
        ## if pagniation needed, use the url below. Defualt is 100
        #GET /api/api-version/sites/site-id/users?pageSize=page-size&pageNumber=page-number
        url = server + "/api/{0}/sites/{1}/users?pageSize=200".format(VERSION, site_id)
        # xml_request = 'none'
        server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
        _check_status(server_response, 200, xmlns)
        server_response = _encode_for_display(server_response.text)
        parsed_response = ET.fromstring(server_response)
        self.users = parsed_response.findall('.//t:user', namespaces=xmlns)
        self.user_names= [user.get('name') for user in self.users]
        self.user_ids= [user.get('id') for user in self.users]

    def user_id_from_name(self, user_name):
        _check_user_input(user_name, self.user_names)
        if user_name in self.user_names:
            user_id = [user.get('id') for user in self.users if user.get('name') == user_name]
        return user_id[0]

    def user_name_from_id(self, user_id):
        _check_user_input(user_id, self.user_ids)
        if user_id in self.user_ids:
            user_name = [user.get('name') for user in self.users if user.get('id') == user_id]
            return user_name[0]
    
    def user_siterole_from_name(self, user_name):
        _check_user_input(user_name, self.user_names)
        if user_name in self.user_names:
            user_siterole = [user.get('siteRole') for user in self.users if user.get('name') == user_name]
            return user_siterole[0]

    def user_lastlogin_from_name(self, user_name):
        _check_user_input(user_name, self.user_names)
        if user_name in self.user_names:
            user_lastlogin = [user.get('lastLogin') for user in self.users if user.get('name') == user_name]
            return user_lastlogin[0]

    def user_exauthid_from_name(self, user_name):
        _check_user_input(user_name, self.user_names)
        if user_name in self.user_names:
            user_exauthid = [user.get('externalAuthUserId') for user in self.users if user.get('name') == user_name]
            return user_exauthid[0]

    def user_langcode_from_name(self, user_name):
        _check_user_input(user_name, self.user_names)
        if user_name in self.user_names:
            user_langcode = [user.get('language') for user in self.users if user.get('name') == user_name]
            return user_langcode[0]

    def user_localecode_from_name(self, user_name):
        _check_user_input(user_name, self.user_names)
        if user_name in self.user_names:
            user_localecode = [user.get('locale') for user in self.users if user.get('name') == user_name]
            return user_localecode[0]

def users_in_group(VERSION, site_id, token, group_id, server, xmlns):
    #GET /api/api-version/sites/site-id/groups/group-id/users
    url = server + "/api/{0}/sites/{1}/groups/{2}/users".format(VERSION, site_id, group_id)
    # xml_request = 'none'
    server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    users = parsed_response.findall('.//t:user', namespaces=xmlns)
    group_users=[]
    for user in users:
        group_users.append(user.get('name'))
    return group_users

def groups_for_user(VERSION, site_id, token, user_id, server, xmlns):
    # GET /api/api-version/sites/site-id/users/user-id/groups
    url = server + "/api/{0}/sites/{1}/users/{2}/groups".format(VERSION, site_id, user_id)
    # # xml_request = 'none'
    server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    groups = parsed_response.findall('.//t:group', namespaces=xmlns)
    user_groups=[]
    for group in groups:
        if group.get('name') != 'All Users':
            user_groups.append(group.get('name'))
    return user_groups

def add_group(VERSION, site_id, token, server, xmlns, group_name, min_site_role = 'Viewer'):
    # POST /api/api-version/sites/site-id/groups
    url = server + "/api/{0}/sites/{1}/groups".format(VERSION, site_id)
    xml_request = ET.Element('tsRequest')
    group_element = ET.SubElement(xml_request, 'group', name=group_name, minimumSiteRole=min_site_role)
    xml_request=ET.tostring(xml_request)
    server_response = requests.post(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 201, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    new_group = parsed_response.findall('.//t:group', namespaces=xmlns)
    for x in new_group:
        group_name= x.get('name')
        group_id= x.get('id')
        minsiterole= x.get('minimumSiteRole')
        print(group_name, group_id, minsiterole) 
    return group_name, group_id, minsiterole

def add_user(VERSION, site_id, token, server, xmlns, user_name, site_role):
    # POST /api/api-version/sites/site-id/users
    url = server + "/api/{0}/sites/{1}/users".format(VERSION, site_id)
    xml_request = ET.Element('tsRequest')
    user_element = ET.SubElement(xml_request, 'user', name=user_name, siteRole=site_role)
    xml_request=ET.tostring(xml_request)
    server_response = requests.post(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 201, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    new_user = parsed_response.findall('.//t:user', namespaces=xmlns)
    for x in new_user:
        user_name= x.get('name')
        site_role= x.get('SiteRole')
        print(user_name, site_role) 
    return user_name, site_role
    
def add_user_to_group(VERSION, site_id, token, server, xmlns, group_id, user_id):
    # /api/api-version/sites/site-id/groups/group-id/users
    url = server + "/api/{0}/sites/{1}/groups/{2}/users".format(VERSION, site_id, group_id)
    xml_request = ET.Element('tsRequest')
    user_element = ET.SubElement(xml_request, 'user', id=user_id)
    xml_request=ET.tostring(xml_request)
    server_response = requests.post(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    new_user = parsed_response.findall('.//t:user', namespaces=xmlns)
    for x in new_user:
        user_name= x.get('name')
        user_id= x.get('id')
        print(user_name, user_id) 
    return user_name, user_id

def create_project(VERSION, site_id, token, server, xmlns, in_project_name, in_description, in_contentpermissions= 'LockedToProject'):
    # POST /api/api-version/sites/site-id/projects
    url = server + "/api/{0}/sites/{1}/projects".format(VERSION, site_id)
    xml_request = ET.Element('tsRequest')
    project_element = ET.SubElement(xml_request, 'project', name = in_project_name, description = in_description, contentPermissions = in_contentpermissions)
    xml_request=ET.tostring(xml_request)
    server_response = requests.post(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 201, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    new_project = parsed_response.findall('.//t:project', namespaces=xmlns)
    for x in new_project:
        id= x.get('id')
        parent_project_id= x.get('parentProjectId')
        new_project_name= x.get('name')
        new_description= x.get('description')
        new_contentpermissions= x.get('contentPermissions')
        controlling_perm_projectid= x.get('controllingPermissionsProjectId')
    print(id, parent_project_id, new_project_name, new_description, new_contentpermissions, controlling_perm_projectid)

def update_project_name(VERSION, site_id, token, server, xmlns, project_id, new_proj_name):
    # PUT /api/api-version/sites/site-id/projects/project-id
    url = server + "/api/{0}/sites/{1}/projects/{2}".format(VERSION, site_id, project_id)
    xml_request = ET.Element('tsRequest')
    #project_element = ET.SubElement(xml_request, 'project', contentPermissions = new_content_permissions, parentProjectId = parent_proj_id, name = new_proj_name, description = new_description)
    project_element = ET.SubElement(xml_request, 'project', name = new_proj_name)
    xml_request=ET.tostring(xml_request)
    server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    print(server_response.status_code)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    new_project = parsed_response.findall('.//t:project', namespaces=xmlns)
    updated_name=  new_project.get('name')
    print(updated_name + " updated")

def update_project_contentpermissions(VERSION, site_id, token, project_id, server, xmlns, new_content_permissions):
    # PUT /api/api-version/sites/site-id/projects/project-id
    if new_content_permissions not in {"LockedToProject", "ManagedByOwner", "LockedToProjectWithoutNested"}:
        raise ValueError("invalid argument content permissions: must be LockedToProject, ManagedByOwner, or LockedToProjectWithoutNested")
    url = server + "/api/{0}/sites/{1}/projects/{2}".format(VERSION, site_id, project_id)
    xml_request = ET.Element('tsRequest')
    #project_element = ET.SubElement(xml_request, 'project', contentPermissions = new_content_permissions, parentProjectId = parent_proj_id, name = new_proj_name, description = new_description)
    project_element = ET.SubElement(xml_request, 'project', contentPermissions = new_content_permissions)
    xml_request=ET.tostring(xml_request)
    server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    new_project = parsed_response.findall('.//t:project', namespaces=xmlns)
    for x in new_project:
        updated_contentpermissions = x.get('contentPermissions')
    print(" updated to " + updated_contentpermissions)

def delete_project(VERSION, site_id, token, server, xmlns, project_id): 
    # DELETE /api/api-version/sites/site-id/projects/project-id
    url = server + "/api/{0}/sites/{1}/projects/{2}".format(VERSION, site_id, project_id)
    # xml_request = none
    server_response = requests.delete(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 204, xmlns)
    server_response = _encode_for_display(server_response.text)

def delete_group(VERSION, site_id, token, server, xmlns, group_id): 
    # DELETE /api/api-version/sites/site-id/groups/group-id
    url = server + "/api/{0}/sites/{1}/groups/{2}".format(VERSION, site_id, group_id)
    # xml_request = none
    server_response = requests.delete(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 204, xmlns)
    server_response = _encode_for_display(server_response.text)

def delete_user(VERSION, site_id, token, server, xmlns, user_id): 
    # DELETE /api/api-version/sites/site-id/users/user-id
    url = server + "/api/{0}/sites/{1}/users/{2}".format(VERSION, site_id, user_id)
    # xml_request = none
    server_response = requests.delete(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 204, xmlns)
    server_response = _encode_for_display(server_response.text)

def remove_user_from_group(VERSION, site_id, token, server, xmlns, group_id, user_id): 
    # DELETE /api/api-version/sites/site-id/groups/group-id/users/user-id
    url = server + "/api/{0}/sites/{1}/groups/{2}/users/{3}".format(VERSION, site_id, group_id, user_id)
    # xml_request = none
    server_response = requests.delete(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 204, xmlns)
    server_response = _encode_for_display(server_response.text)

def update_user(VERSION, site_id, token, server, xmlns, user_id, new_name, new_email, new_password, new_siterole):
    # PUT /api/api-version/sites/site-id/users/user-id
    url = server + "/api/{0}/sites/{1}/users/{2}".format(VERSION, site_id, user_id)
    xml_request = ET.Element('tsRequest')
    user_element = ET.SubElement(xml_request, 'user', fullName = new_name, email = new_email, password = new_password, siteRole = new_siterole)  
    xml_request=ET.tostring(xml_request)
    server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)

from collections import defaultdict

def nested_dict():
   return defaultdict(nested_dict)

class QueryDefaultPermissions():
    def __init__(self, VERSION, site_id, token, server, xmlns, project_id):
        """
        creates nested dictionary of default permissions for project (project, workbook, datasource, flow, metric)
        nested dict can be queried via associated methods for example:

        {
    "groups": {
        "groupuuid": {
            "datasource": {},
            "flow": {},
            "metric": {},
            "project": {
                "Read": "Allow"
            },
            "workbook": {
                "AddComment": "Allow",
                "ExportData": "Allow",
                "ExportImage": "Allow",
                "Filter": "Allow",
                "Read": "Allow",
                "ShareView": "Allow",
                "ViewComments": "Allow",
                "ViewUnderlyingData": "Allow",
                "WebAuthoring": "Allow"
            }
        },
    "users": {
        "useruuid": {
            "datasource": {},
            "flow": {},
            "metric": {},
            "project": {
                "Read": "Allow"
            },
            "workbook": {
                "AddComment": "Allow",
                "ExportData": "Allow",
                "ExportImage": "Allow",
                "Filter": "Allow",
                "Read": "Allow",
                "ShareView": "Allow",
                "ViewComments": "Allow",
                "ViewUnderlyingData": "Allow",
                "WebAuthoring": "Allow"
            }
        }
        """
        self.VERSION = VERSION
        self.site_id = site_id
        self.project_id = project_id
        self.server = server
        self.xmlns = xmlns
        perm_dict = nested_dict()
        for permissions_obj in {"project", "workbook", "datasource", "flow", "metric"}:
            if permissions_obj == "project":
                #  GET /api/api-version/sites/site-id/projects/project-id/permissions
                url = server + "/api/{0}/sites/{1}/projects/{2}/permissions".format(VERSION, site_id, project_id)
            else:
                #  GET /api/api-version/sites/site-id/projects/project-id/default-permissions/{permissions_obj}s
                url = server + "/api/{0}/sites/{1}/projects/{2}/default-permissions/{3}s".format(VERSION, site_id, project_id, permissions_obj)
            # xml_request = 'none'
            server_response = requests.get(url, headers={'x-tableau-auth': token}, verify=False)
            _check_status(server_response, 200, xmlns)
            server_response = _encode_for_display(server_response.text)
            parsed_response = ET.fromstring(server_response)
            grantee_capabilities = parsed_response.findall('.//t:granteeCapabilities', namespaces=xmlns)
            for gr_cap in grantee_capabilities:
                users = gr_cap.findall('.//t:user', namespaces=xmlns)
                if users is not None:
                    for user in users:
                        userid=user.get("id")
                        capabilities=gr_cap.findall('.//t:capability', namespaces=xmlns)
                        for cap in capabilities:
                            cap_name=cap.get('name')
                            cap_mode=cap.get('mode')
                            perm_dict['users'][userid][permissions_obj][cap_name]=cap_mode
                groups = gr_cap.findall('.//t:group', namespaces=xmlns)
                if groups is not None:
                    for group in groups:
                        groupid=group.get("id")
                        capabilities=gr_cap.findall('.//t:capability', namespaces=xmlns)
                        for cap in capabilities:
                            cap_name=cap.get('name')
                            cap_mode=cap.get('mode')
                            perm_dict['groups'][groupid][permissions_obj][cap_name]=cap_mode
        self.perm_dict= perm_dict

        all_allow_users=set()
        for user in self.perm_dict['users'].keys():
            for permissions_obj in {"project", "workbook", "datasource", "flow", "metric"}:
                all_allow_users.update(set([user for cap_name in self.perm_dict['users'][user][permissions_obj].keys() if self.perm_dict['users'][user][permissions_obj][cap_name] == 'Allow']))
        self.all_allow_users=all_allow_users

        all_allow_groups=set()
        for group in self.perm_dict['groups'].keys():
            for permissions_obj in {"project", "workbook", "datasource", "flow", "metric"}:
                all_allow_groups.update(set([group for cap_name in self.perm_dict['groups'][group][permissions_obj].keys() if self.perm_dict['groups'][group][permissions_obj][cap_name] == 'Allow']))
        self.all_allow_groups=all_allow_groups

    def query_permissions(self, permissions_obj, users_or_groups, capability_mode): 
        allow_groups_or_users=set()
        if permissions_obj not in {"project", "workbook", "datasource", "flow", "metric"}:
            raise ValueError("invalid argument: must be one of %r." % {"project", "workbook", "datasource", "flow", "metric"})
        else:
            for user_or_group in self.perm_dict[users_or_groups].keys():
                allow_groups_or_users.update(set([user_or_group for cap_name in self.perm_dict[users_or_groups][user_or_group][permissions_obj].keys() if self.perm_dict[users_or_groups][user_or_group][permissions_obj][cap_name] == capability_mode]))
        return allow_groups_or_users



class WriteDefaultPermissions():
    """
    VERSION: global variable of rest api version e.g '3.11'
    site_id, token should always be saved when returned from tableau_rest.sign_in()
    can add permissions via a dictionary
    dictionary can be queried from a master permissions object, or can be created using the helper function create_permisions_dict
    """
    def __init__(self, VERSION, site_id, token, server, xmlns, permissions_obj, proj_id):
        if permissions_obj not in {"project", "workbook", "datasource", "flow", "metric"}:
            raise ValueError("invalid argument: must be one of %r." % {"project", "workbook", "datasource", "flow", "metric"})
        else:
            self.token = token
            self.VERSION = VERSION
            self.site_id = site_id
            self.permissions_obj = permissions_obj
            self.proj_id = proj_id
            self.server = server
            self.xmlns = xmlns
    
    def create_permissions_dict(self, user_id_list=[], user_cap_name_list=[], user_cap_mode_list=[], group_id_list=[], group_cap_name_list=[], group_cap_mode_list=[]):
        perm_dict = nested_dict()
        if len(user_id_list)>0:
            zipped_users=zip(user_id_list, user_cap_name_list, user_cap_mode_list)
            for user_id, user_cap_name, user_cap_mode in zipped_users:
                perm_dict['users'][user_id][self.permissions_obj][user_cap_name]=user_cap_mode
        if len(group_id_list)>0:
            zipped_groups=zip(group_id_list, group_cap_name_list, group_cap_mode_list)
            for group_id, group_cap_name, group_cap_mode in zipped_groups:
                perm_dict['groups'][group_id][self.permissions_obj][group_cap_name]=group_cap_mode
        return perm_dict

    def add_permissions(self, perm_dict):
        if self.permissions_obj == "project":
            # PUT /api/api-version/sites/site-id/projects/project-id/permissions
            url = self.server + "/api/{0}/sites/{1}/projects/{2}/permissions".format(self.VERSION, self.site_id, self.proj_id)
        else:
            # PUT /api/api-version/sites/site-id/projects/project-id/default-permissions/workbooks
            url = self.server + "/api/{0}/sites/{1}/projects/{2}/default-permissions/{3}s".format(self.VERSION, self.site_id, self.proj_id, self.permissions_obj)
        xml_request = ET.Element('tsRequest')
        permissions_element= ET.SubElement(xml_request, 'permissions')
        if "users" in perm_dict.keys():
            for user_id in perm_dict['users'].keys():
                grantee_element= ET.SubElement(permissions_element, 'granteeCapabilities')
                user_element = ET.SubElement(grantee_element, 'user', id=user_id)
                capabilities_element= ET.SubElement(grantee_element, 'capabilities')
                for cap_name in perm_dict['users'][user_id][self.permissions_obj].keys():
                    ET.SubElement(capabilities_element, 'capability', name=cap_name, mode=perm_dict['users'][user_id][self.permissions_obj][cap_name])
        if "groups" in perm_dict.keys():
            for group_id in perm_dict['groups'].keys():
                grantee_element= ET.SubElement(permissions_element, 'granteeCapabilities')
                group_element = ET.SubElement(grantee_element, 'group', id=group_id)
                capabilities_element= ET.SubElement(grantee_element, 'capabilities')
                for cap_name in perm_dict['groups'][group_id][self.permissions_obj].keys():
                    ET.SubElement(capabilities_element, 'capability', name=cap_name, mode=perm_dict['groups'][group_id][self.permissions_obj][cap_name])
        xml_request=ET.tostring(xml_request)
        server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': self.token}, verify=False)
        _check_status(server_response, 200, self.xmlns)
        server_response = _encode_for_display(server_response.text)
        parsed_response = ET.fromstring(server_response)
        users = parsed_response.findall('.//t:user', namespaces=self.xmlns)
        if users is not None:
            for user in users:
                userid=user.get("id")
                new_capabilities=parsed_response.findall('.//t:capability', namespaces=self.xmlns)
                for cap in new_capabilities:
                    cap_name=cap.get('name')
                    cap_mode=cap.get('mode')
                print("New user " + self.permissions_obj + " permissions: " + userid + ' ' + cap_name + ' ' + cap_mode)
        groups = parsed_response.findall('.//t:group', namespaces=self.xmlns)
        if groups is not None:
            for group in groups:
                groupid=group.get("id")
                new_capabilities=parsed_response.findall('.//t:capability', namespaces=self.xmlns)
                for cap in new_capabilities:
                    cap_name=cap.get('name')
                    cap_mode=cap.get('mode')
                print("New group " + self.permissions_obj + " permissions: " + groupid + ' ' + cap_name + ' ' + cap_mode)
    
    def delete_permissions(self, perm_dict):
        for group_or_user in perm_dict.keys():
            for id in perm_dict[group_or_user].keys():
                for cap_name in perm_dict[group_or_user][id][self.permissions_obj].keys():
                    cap_mode = perm_dict[group_or_user][id][self.permissions_obj][cap_name]
                    if self.permissions_obj != "project":
                        # DELETE /api/api-version/sites/site-id/projects/project-id/default-permissions/workbooks/groups/group-id/capability-name/capability-mode
                        url = self.server + "/api/{0}/sites/{1}/projects/{2}/default-permissions/{3}s/{4}/{5}/{6}/{7}".format(self.VERSION, self.site_id, self.proj_id, self.permissions_obj, group_or_user, id, cap_name, cap_mode)
                    elif self.permissions_obj == "project":
                        # DELETE /api/api-version/sites/site-id/projects/project-id/permissions/users/user-id/capability-name/capability-mode
                        url = self.server + "/api/{0}/sites/{1}/projects/{2}/permissions/{3}/{4}/{5}/{6}".format(self.VERSION, self.site_id, self.proj_id, group_or_user, id, cap_name, cap_mode)
                    # xml_request = none
                    server_response = requests.delete(url, headers={'x-tableau-auth': self.token}, verify=False)
                    _check_status(server_response, 204, self.xmlns)
                    print(group_or_user + ' ' + id + " permission deleted from " + self.proj_id)


def add_user_permission_to_project(VERSION, site_id, token, server, xmlns, project_id, user_id, cap_name, cap_mode):
    # PUT /api/api-version/sites/site-id/projects/project-id/permissions
    url = server + "/api/{0}/sites/{1}/projects/{2}/permissions".format(VERSION, site_id, project_id)
    xml_request = ET.Element('tsRequest')
    permissions_element= ET.SubElement(xml_request, 'permissions')
    grantee_element= ET.SubElement(permissions_element, 'granteeCapabilities')
    ### for userids in list - maybe dictionary??
    user_element = ET.SubElement(grantee_element, 'user', id=user_id)
    capabilities_element= ET.SubElement(grantee_element, 'capabilities')
    ET.SubElement(capabilities_element, 'capability', name=cap_name, mode=cap_mode)
    xml_request=ET.tostring(xml_request)
    print(xml_request)
    server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 200, xmlns)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    user = parsed_response.findall('.//t:user', namespaces=xmlns)
    for x in user:
        user=x.get("id")
    new_capabilities = parsed_response.findall('.//t:capability', namespaces=xmlns)
    for cap in new_capabilities:
        new_cap= cap.get('name')
        new_mode= cap.get('mode')
        print(new_cap, new_mode, user) 
    return new_cap, new_mode, user

def delete_user_permission_from_project(VERSION, site_id, token, server, xmlns, project_id, user_id, cap_name, cap_mode):
    # DELETE /api/api-version/sites/site-id/projects/project-id/permissions/users/user-id/capability-name/capability-mode
    url = server + "/api/{0}/sites/{1}/projects/{2}/permissions/users/{3}/{4}/{5}".format(VERSION, site_id, project_id, user_id, cap_name, cap_mode)
    # xml_request = none
    server_response = requests.delete(url, headers={'x-tableau-auth': token}, verify=False)
    _check_status(server_response, 204, xmlns)
    return print(user_id + " permission deleted from " + project_id)



