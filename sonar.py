import sonarqube
import sonarqube.utils.exceptions as sq_exceptions
import requests
from requests.auth import HTTPBasicAuth
from typing import List


class Sonarqube:
    RO_PERMISSION = ['user', 'codeviewer']
    RW_PERMISSION = ['user', 'codeviewer', 'scan']

    def __init__(self, token: str, url: str) -> None:
        self._sonarqube = sonarqube.SonarEnterpriseClient(sonarqube_url=url, token=token, verify=True)
        self._auth = HTTPBasicAuth(f'{token}', '')
        self._url = url
        print('Credential validity: ', end='')
        print(self._sonarqube.auth.check_credentials())
        self.all_sonar_users = list(self._sonarqube.users.search_users()['users'])
        self.all_sonar_users = [user for user in self.all_sonar_users if 'email' in user]
        self.all_sonar_projects = self._sonarqube.projects.search_projects()['components']
        self.all_sonar_projects = [project for project in self.all_sonar_projects if 'key' in project]
        self.all_sonar_groups = self._sonarqube.user_groups.search_user_groups()['groups']
        self.all_sonar_groups = [group for group in self.all_sonar_groups if 'name' in group]

    def set_user_permission(self, user_names: List[str], projects_name: List[str], permission: str):
        print("Start permission settings for user(s).")
        user_endpoint_url = "api/permissions/add_user"
        if permission == "ro":
            for access in self.RO_PERMISSION:
                for user in user_names:
                    for project in projects_name:
                        requests.post(f'{self._url}{user_endpoint_url}?login={user}&permission={access}&projectKey={project}', auth=self._auth)
        else:
            for access in self.RW_PERMISSION:
                for user in user_names:
                    for project in projects_name:
                        requests.post(f'{self._url}{user_endpoint_url}?login={user}&permission={access}&projectKey={project}', auth=self._auth)

    def set_group_permission(self, group_names: List[str], projects_name: List[str], permission: str):
        print("Start permission settings for group(s).")
        group_endpoint_url = "api/permissions/add_group"
        if permission == "ro":
            for access in self.RW_PERMISSION:
                for group in group_names:
                    for project in projects_name:
                        requests.post(f'{self._url}{group_endpoint_url}?login={group}&permission={access}&projectKey={project}', auth=self._auth)
        else:
            for access in self.RW_PERMISSION:
                for group in group_names:
                    for project in projects_name:
                        requests.post(f'{self._url}{group_endpoint_url}?login={group}&permission={access}&projectKey={project}', auth=self._auth)
    
    def validate_projects_case_insensitive(self, projects_name: List[str]) -> None:
        print('\n\nStarting project validations')
        invalid_projects = []
        for project_names in set(projects_name):
            print(f'Validating projects: {project_names} ', end='')
            for sonar_projects in self.all_sonar_projects:
                if sonar_projects['key'].lower() == project_names.lower():
                    print('\nProject found.')
                    break
            else:
                print('\nProject not found.')
                invalid_projects.append(project_names)

        if invalid_projects:
            print(f'ERROR: The following projects are not found in SonarQube: {invalid_projects}')
            raise sq_exceptions.ValidationError("Project validation error.")
        else:
            print(f'Project validation successful.')

    def validate_users_case_insensitive(self, user_emails: List[str]) -> None:
        print('\n\nStarting user validations')
        invalid_users = []
        for user_email in set(user_emails):
            print(f'Validating user: {user_email}. ', end='')
            for sonar_user in self.all_sonar_users:
                if sonar_user['email'].lower() == user_email.lower():
                    print('User found.')
                    break
            else:
                print('User not found.')
                invalid_users.append(user_email)

        if invalid_users:
            print(f'ERROR: The following users are not found in SonarQube: {invalid_users}')
            raise sq_exceptions.ValidationError("User validation error.")
        else:
            print('User validation successful.')

    def validate_groups_case_insensitive(self, groups_name: List[str]) -> None:
        print('\n\nStarting group validations')
        invalid_groups = []
        for group_names in set(groups_name):
            print(f'Validating groups: {group_names} ', end='')
            for sonar_groups in self.all_sonar_groups:
                if sonar_groups['name'].lower() == group_names.lower():
                    print('\Group found.')
                    break
            else:
                print('\Group not found.')
                invalid_groups.append(group_names)

        if invalid_groups:
            print(f'ERROR: The following groups are not found in SonarQube: {invalid_groups}')
            raise sq_exceptions.ValidationError("Group validation error.")
        else:
            print(f'Group validation successful.')

    def get_user_emails_with_correct_case(self, user_emails: List[str]) -> List[str]:
        correct_emails = []
        for user_email in set(user_emails):
            for sonar_user in self.all_sonar_users:
                if sonar_user['email'].lower() == user_email.lower():
                    correct_emails.append(sonar_user['email'])
                    break
            else:
                print(f'Could not get user email with correct case: {user_email}')
                raise Exception(f'Could not get user email with correct case: {user_email}')
        return correct_emails

    def get_project_names_with_correct_case(self, projects_name: List[str]) -> List[str]:
        correct_projects = []
        for project_name in set(projects_name):
            for sonar_project in self.all_sonar_projects:
                if sonar_project['key'].lower() == project_name.lower():
                    correct_projects.append(sonar_project['key'])
                    break
            else:
                print(f'Could not get project name with correct case: {project_name}')
                raise Exception(f'Could not get project name with correct case: {project_name}')
        return correct_projects

    def get_group_names_with_correct_case(self, groups_name: List[str]) -> List[str]:
        correct_groups = []
        for group_name in set(groups_name):
            for sonar_group in self.all_sonar_groups:
                if sonar_group['name'].lower() == group_name.lower():
                    correct_groups.append(sonar_group['name'])
                    break
            else:
                print(f'Could not get group name with correct case: {group_name}')
                raise Exception(f'Could not get group name with correct case: {group_name}')
        return correct_groups

    def get_user_login_names(self, user_emails: List[str]) -> List[str]:
        login_names = []
        for user_email in set(user_emails):
            sonar_users = self._sonarqube.users.search_users(q=user_email)['users']
            for sonar_user in sonar_users:
                if sonar_user['email'] == user_email:
                    login_names.append(sonar_user['login'])
                    break
        return login_names

    def get_project_names(self, projects_name: List[str]) -> List[str]:
        prj_names = []
        for prj_name in set(projects_name):
            sonar_projects = self._sonarqube.projects.search_projects(q=prj_name)['components']
            for sonar_project in sonar_projects:
                if sonar_project['key'] == prj_name:
                    prj_names.append(sonar_project['key'])
                break
        return prj_names

    def get_group_names(self, groups_name: List[str]) -> List[str]:
        group_names = []
        for group_name in set(groups_name):
            sonar_groups = self._sonarqube.user_groups.search_user_groups(q=group_name)['groups']
            for sonar_group in sonar_groups:
                if sonar_group['name'] == group_name:
                    group_names.append(sonar_group['name'])
                break
        return group_names
