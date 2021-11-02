# tabula
A python package for automating tableau administrative tasks using the tableau REST api

## tableau_rest functionality and examples
tableau_rest is a python module that uses the requests package to interact with the [Tableau Rest API](https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm). 
Functionality of the module includes: creating API request URLs, building out XML request elements using the python elementtree package, sending API requests using the python requests package, checking the request response for errors and parsing the response XML to return useful information.
Classes are designed to minimize the number API calls; each class represents an XML response and each class variable/method parses the XML response. This module may be used for adding/syncing/auditing users and groups, adding/syncing/auditing projects and workbooks, and adding/syncing/auditing default project permissions.


### Table of Contents
1. [Login](#login)
2. [QueryProjects](#queryprojects)
3. [QueryWorkbooks](#queryworkbooks)
4. [QueryWorkbookViews](#queryworkbookviews)
5. [QueryGroups](#queryworkbookviews)
6. [QueryUsers](#queryworkbookviews)
7. [QueryDefaultPermissions](#querydefaultpermissions)
8. [WriteDefaultPermissions](#writedefaultpermissions)
9. [Other Functions](#other-functions)
    - [Users in group](#users-in-group)
    - [Groups for user](#groups-for-user)
    - [Add group](#add-group)
    - [Add user](#add-user)
    - [Add user to group](#add-user-to-group)
    - [Create project](#create-project)
    - [Update project name](#update-project-name)
    - [Update project content permissions](#update-project-content-permissions)
    - [Delete project](#delete-project)
    - [Delete group](#delete-group)
    - [Delete user](#delete-user)
    - [Remove user from group](#remove-user-from-group)
    - [Update user](#update-user)
    - [Add user permission to project](#add-user-permission-to-project)
    - [Delete user permission from project](#delete-user-permission-from-project)


#### Login
- log in to the Tableau REST server and store token, siteid and your userid for use in other methods
  ```
  server= "https://tableau.example.com"
  username= "tableauusername"
  password= "tableaupassword"
  ##if there is only one site you can leave this blank, otherwise specify site
  site = ''
  ## version of tableau REST API
  VERSION= '3.11'
  ## namespaces for API calls to the tableau server
  xmlns = {'t': 'http://tableau.com/api'}
  ```
  ```
  # store token, site_id and user_id to use for other methods
  token, site_id, my_user_id = tableau_rest.sign_in(server, username, password, VERSION, xmlns, site)
  ```
- log out
  ```
  tableau_rest. sign_out(server, VERSION, xmlns)
  ```
#### QueryProjects
- create QueryProjects class object
  ```
  projects_obj=tableau_rest.QueryProjects(VERSION, site_id, token, server, xmlns)
  ```
- variables in QueryProjects class
  ```
  # returns list of project names
  projects_obj.project_names
  # returns list of project ids 
  projects_obj.project_ids
  ```
- methods in QueryProjects class
  ```
  # returns project id given a project name. Many API calls use project id; can store project id as a variable to use for other methods
  projects_obj.project_id_from_name("server project name")
  
  # returns project name on the server for a given project uuid
  projects_obj.project_id_from_name('12345678exampleprojid')
  
  # returns project description on server for a given project name
  projects_obj.project_description_from_name("server project name")
  
  # returns project controlling permissions on server for a given project name
  projects_obj.project_controllingpermissions_from_name("server project name")
  
  # returns project created at date on server for a given project name
  projects_obj.project_createdat_from_name("server project name")
  
  # returns project updated at date on server for a given project name
  projects_obj.project_updatedat_from_name("server project name")
  
  # returns "True" if project permissions are locked and "False" if project permissions are not locked for a given project name
  projects_obj.project_permissionslocked_from_name("server project name")
  ```
#### QueryWorkbooks
- create QueryWorkbooks class object
  ```
  workbook_obj=tableau_rest.QueryWorkbooks(VERSION, site_id, token, server, xmlns)
  ```
- variables in QueryWorkbooks class
  ```
  # returns list of all workbook names on server
  workbooks_obj.workbook_names
  # returns list of all workbook ids on server
  workbooks_obj.workbook_ids
  ```
- methods in QueryWorkbooks class
  ```
  # returns workbook id on server given a workbook name
  workbooks_obj.workbook_id_from_name("workbook name")
  
  # returns workbook name on server given a workbook uuid
  workbooks_obj.workbook_name_from_id("98765432examplewbid")
  
  # returns a list of workbook names that belong to a specific project, given the project id
  workbooks_obj.workbooks_from_projectid("12345678exampleprojid")
  ```
#### QueryWorkbookViews
- create QueryWorkbookViews class object
  ```
  wb_views_obj=tableau_rest.QueryWorkbookViews(VERSION, site_id, token, server, xmlns, workbook_id)
  ```
- variables in QueryWorkbooks class
  ```
  # returns a list of all view names in workbook
  wb_views_obj.view_names
  # returns a list all view ids in workbook
  wb_views_obj.view_ids
  ```
- methods in QueryWorkbookViews class
  ```
  # returns view id given the view name
  wb_views_obj.view_id_from_name("my view name")
  # returns view name given the view uuid on the server
  wb_views_obj.view_name_from_id("1928374656exampleviewid")
  # returns the content url for the view given the view id
  wb_views_obj.view_contenturl_from_id("1928374656exampleviewid")
  ```
#### QueryGroups
- create QueryGroups class object
  ```
  groups_obj=tableau_rest.QueryGroups(VERSION, site_id, token, server, xmlns)
  ```
- variables in QueryGroups class
  ```
  # returns a list of all group names on server
  groups_obj.group_names
  # returns a list of all group ids on server
  groups_obj.group_ids
  ```
- methods in QueryGroups class
  ```
  # returns group id given the group name
  groups_obj.group_id_from_name("my group name")
  # returns group name given the group uuid on the server
  groups_obj.group_name_from_id("1357908642groupid")
  ```
#### QueryUsers
- create QueryUsers class object
  ```
  users_obj=tableau_rest.QueryUsers(VERSION, site_id, token, server, xmlns)
  ```
- variables in QueryUsers class
  ```
  # returns a list of all user names on server
  users_obj.user_names
  # returns a list of all user ids on server
  users_obj.user_ids
  ```
- methods in QueryUsers class
  ```
  # returns user uuid based on user name
  users_obj.user_id_from_name("my user name")
  # returns user name from user id
  users_obj.user_name_from_id("222444666userid")
  # return site role from user name
  tableau_rest.user_siterole_from_name("my user name")
  # return last login date from user name
  tableau_rest.user_lastlogin_from_name("my user name")
  # returns external auth id from user name
  tableau_rest.user_exauthid_from_name("my user name")
  # returns language code from user name
  tableau_rest.user_langcode_from_name("my user name")
  # returns locale code from user name
  tableau_rest.user_localecode_from_name("my user name")
  ```
#### QueryDefaultPermissions
This class queries the default permissions for a project on the tableau server. Permissions are described in terms of user or group *capabilities* and user or group *modes*. Permissions content types are: project, workbook, datasource, flow and metric. More information on Tableau permissions can be found in the Tableau documention [here](https://help.tableau.com/current/server/en-us/permissions_capabilities.htm)

project: part of project permissions (not default permissions). Valid capabilities are *Read* and *Write*

workbook: sets default workbook permissions for all workbooks in the project. Valid default workbook permission capabilities are *AddComment*, *ChangeHierarchy*, *ChangePermissions*, *Delete*, *ExportData*, *ExportImage*, *ExportXml*, *Filter*, *Read*, *ShareView*, *ViewComments*, *ViewUnderlyingData*, *WebAuthoring*, and *Write*
datasource: sets default datasource permissions in the project. Valid default datasource permission capabilities are *ChangePermissions*, *Connect*, *Delete*, *ExportXml*, *Read*, and *Write*.
flow: sets default flow permissions in the project. Valid flow capabilities are *ChangeHierarchy*, *ChangePermissions*, *Delete*, *Execute*, *ExportXml*, *Read*, and *Write*

metric: sets the default metric permissions in the project. Valid metric capabilities include *View* and probably others, but there is no documentation on the offical Tableau REST API re: using the REST API for this content type- I usually leave empty. Data Roles is another permissions type that doesn't have any documentation on the capabilities for the API

Valid modes are *Deny* and *Allow*

QueryDefaultPermissions class returns all default project permissions as a nested dictionary in the following format

  ```
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
  ```
        
- create QueryDefaultPermissions class object
  ```
  defaultperms_obj=tableau_rest.QueryDefaultPermissions(VERSION, site_id, token, server, xmlns, project_id)
  ```
- variables in QueryDefaultPermissions class
  ```
  # creates nested dictionary of default permissions for the project
  defaultperms_obj.perm_dict
  # returns a list of all the users on the site that have any "Alow" permissions
  defaultperms_obj.all_allow_users
  # returns a list of all the groups on the site that have any "Alow" permissions
  defaultperms_obj.all_allow_groups
  ```
- methods in QueryDefaultPermissions class
  ```
  # Returns a list of users or groups that have ANY allow/deny capabilities for the specified permissions content type
  # Permissions content type valid inputs: project, workbook, datasource, flow or metric
  # users_or_groups valid inputs: users or groups
  # capability_mode valid inputs: Allow or Deny
  
  defaultperms_obj.query_permissions(permissions_content_type, users_or_groups, capability_mode)
  # for example: 
  defaultperms_obj.query_permissions("project", "groups", "Allow")
  ```
#### WriteDefaultPermissions
Using this class you can: create a formatted default permissions dictionary, add permissions to the server using a dictionary, remove permissions from the server using a dictionary

On the Tableau server, existing permissions must be deleted before you can update/add new permissions

- create WriteDefaultPermissions class object
  ```
  # valid permissions_content_type inputs: project, workbook, datasource, flow, metric 
  defaultperms_obj=tableau_rest.QueryDefaultPermissions(VERSION, site_id, token, server, xmlns, permissions_content_type, proj_id)
  
  # for example
  project_id = projects_obj.project_id_from_name("project name")
  writedefaultperms_obj=tableau_rest.WriteDefaultPermissions(VERSION, site_id, token, server, xmlns, "workbook", project_id)
  ```
- methods in WriteDefaultPermissions class
  ```
  # creates permissions dictionary based on lists. By default input is an empty list
  # valid project capabilities:  'Read', 'Write'
  # valid workbook capabilities: 'AddComment', 'ChangeHierarchy', 'ChangePermissions', 'Delete', 'ExportData', 'ExportImage', 'ExportXml', 'Filter', 'Read',  
  # 'ShareView', 'ViewComments', 'ViewUnderlyingData', 'WebAuthoring', 'Write'
  # valid datasource capabilities = 'ChangePermissions', 'Connect', 'Delete', 'ExportXml', 'Read', 'Write'
  # valid capability modes: 'Allow', 'Deny'
  writedefaultperms_obj.create_permissions_dict(user_id_list, user_cap_name_list, user_cap_mode_list, group_id_list, group_cap_name_list, group_cap_mode_list)
  
  # for example
    user_id_list =["user1", "user2"]
    user_cap_name_list=['AddComment', 'ChangeHierarchy']
    user_cap_mode_list=["Allow", "Deny"]
    group_id_list=["group1"]
    group_cap_name_list=["Delete"]
    group_cap_mode_list=["Allow"]
    default_proj_permissions_dict = writedefaultperms_obj.create_permissions_dict(user_id_list, user_cap_name_list, user_cap_mode_list, group_id_list,        
    group_cap_name_list, group_cap_mode_list)
   
  # adds default permissions to sever based on project name from WriteDefaultPermissions object 
  writedefaultperms_obj.add_permissions(default_proj_permissions_dict)
  # deletes default permissions to sever based on project name from WriteDefaultPermissions object
  writedefaultperms_obj.delete_permissions(default_proj_permissions_dict)
  ```
#### Other Functions
##### Users in group
- Returns a list of users for the given group_id
    ```
    group_id = groups_obj.group_id_from_name("my group name")
    tableau_rest.users_in_group(VERSION, site_id, token, group_id, server, xmlns)
    ```
##### Groups for user
- Returns a list of groups for the given user_id
    ```
    user_id = users_obj.user_id_from_name("my user name")
    tableau_rest.groups_for_user(VERSION, site_id, token, user_id, server, xmlns)
    ```
##### Add group
- Adds a group to the server for the given group name. By default, min_site_role = 'Viewer'. Returns the group name, group id and minimum site role. Note that results of QueryGroups are cached so a new group may not be immediately queryable 
    ```
    groupname, groupid, minsiterole = tableau_rest.add_group(VERSION, site_id, token, server, xmlns, "my new group name", min_site_role = 'Viewer')
    ```
##### Add user
- Adds user to the server for the given name and site role. Returns user name and site role. Note that results of QueryUsers are cached so a new group may not be immediately queryable 
    ```
    username, siterole = tableau_rest.add_user(VERSION, site_id, token, server, xmlns, "my new user name", 'Viewer')
    ```
##### Add user to group
- adds a user to a group for the given user id and group id. Returns user name and user id. Note that results of QueryGroups are cached so a new group may not be immediately queryable 
    ```
    group_id = groups_obj.group_id_from_name("my group name")
    user_id = users_obj.user_id_from_name("my user name")
    username, userid = tableau_rest.add_user_to_group(VERSION, site_id, token, server, xmlns, group_id, user_id)
    ```
##### Create project
- create a new project on the server given the project name, description. Content permissions types are "LockedToProject", "ManagedByOwner", "LockedToProjectWithoutNested". By default new project content permissions are set to "LockedToProject"
    ```
    tableau_rest.create_project(VERSION, site_id, token, server, xmlns, "Project Name", "this is a description for my project", in_contentpermissions= 'LockedToProject')
    ```
##### Update project name
- updates a project name on the server given the project id. Doesn't return anything
   ```
    project_id = projects_obj.project_id_from_name("server project name")
    tableau_rest.update_project_name(VERSION, site_id, token, server, xmlns, project_id, "New name for project")
    ```
##### Update project content permissions
- Updates a projects content permissions given the project id. Content permissions types are "LockedToProject", "ManagedByOwner", "LockedToProjectWithoutNested". Function doesn't return anything
   ```
    project_id = projects_obj.project_id_from_name("server project name")
    tableau_rest.update_project_contentpermissions(VERSION, site_id, token, server, xmlns, project_id, 'LockedToProject')
    ```
##### Delete project
- deletes project on the server for a given project id. Doesn't return anything
   ```
    project_id = projects_obj.project_id_from_name("server project name")
    tableau_rest.delete_project(VERSION, site_id, token, server, xmlns, project_id)
    ```
##### Delete group
- deletes group on the server for a given group id. Doesn't return anything
    ```
    group_id = groups_obj.group_id_from_name("my group name")
    tableau_rest.delete_group(VERSION, site_id, token, server, xmlns group_id)
    ```
##### Delete user
- deletes user on the server for a given user id. Doesn't return anything
    ```
    user_id = users_obj.user_id_from_name("my user name")
    tableau_rest.delete_user(VERSION, site_id, token, server, xmlns user_id)
    ```
##### Remove user from group
- removes user from group for the given user id and group id
    ```
    user_id = users_obj.user_id_from_name("my user name")
    group_id = groups_obj.group_id_from_name("my group name")
    tableau_rest.remove_user_from_group(VERSION, site_id, token, server, xmlns, group_id, user_id)
    ```
##### Update user
- updates a user on the server base on user name, email, password and/or site role, for the given user id
    ```
    user_id = users_obj.user_id_from_name("my user name")
    tableau_rest.update_user(VERSION, site_id, token, server, xmlns user_id, "new user name", "newemail@email.com", "newverysecurepassword", "Viewer")
    ```
##### Add user permission to project
- adds a single user permission to a project (does not set default permissions for workbooks, flows etc) based on project id, user id, capability name ("Write", "Read") and capability mode ("Allow", "Deny"). Returns new capability name, new capability mode and user id
   ```
    project_id = projects_obj.project_id_from_name("server project name")
    user_id = users_obj.user_id_from_name("my user name")
    tableau_rest.add_user_permission_to_project(VERSION, site_id, token, server, xmlns, project_id, user_id, "Write", "Allow")
    ```
##### Delete user permission from project
- deletes a single user permission from a project (does not delete default permissions for workbooks, flows etc) based on project id, user id, capability name ("Write", "Read") and capability mode ("Allow", "Deny"). Doesn't return anything
   ```
    project_id = projects_obj.project_id_from_name("server project name")
    user_id = users_obj.user_id_from_name("my user name")
    tableau_rest.delete_user_permission_from_project(VERSION, site_id, token, server, xmlns, project_id, user_id, "Read", "Allow")
    ```

