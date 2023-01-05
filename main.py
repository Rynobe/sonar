import sys
import argparse
from typing import List
from sonar import Sonarqube

SONARQUBE_ENV_CONFIG = {
    'test':
    {
        'url': 'http://127.0.0.1:9000/',
    }
}

parser = argparse.ArgumentParser(description='SonarQube permission script parameters.')
parser.add_argument('sonarqube_auth_token', type=str, help='Technical user token with admin privileges.')
parser.add_argument('--project_names', type=str, help='List of project(s) name. Separated by comma or space.')
parser.add_argument('--ro_emails', type=str, help=f'List of email addresses of the users to add to project(s) with RO permission. Separated by comma or space.')
parser.add_argument('--rw_emails', type=str, help=f'List of email addresses of the users to add to project(s) with RW permission. Separated by comma or space.')
parser.add_argument('--ro_groups', type=str, help=f'List of groups to add to project(s) with RO permission. Separated by comma or space.')
parser.add_argument('--rw_groups', type=str, help=f'List of groups to add to project(s) with RW permission. Separated by comma or space.')

args = parser.parse_args()

def set_permission():

    # Parse inputs
    try:
        print('\n')
        print('Parsing rw users. ', end='')
        rw_users = get_parsed_list(args.rw_emails)
        print('Parsing ro users. ', end='')
        ro_users = get_parsed_list(args.ro_emails)
        print('Parsing project(s) name. ', end='')
        projects = get_parsed_list(args.project_names)
        print('Parsing ro groups. ', end='')
        ro_groups = get_parsed_list(args.ro_groups)
        print('Parsing rw groups. ', end='')
        rw_groups = get_parsed_list(args.rw_groups)
    except Exception as e:
        print('Error when parsing inputs.')
        print(e)
        raise e

    # Set Permission
    try:
        env = []
        env.append(SONARQUBE_ENV_CONFIG['test'])
        for sonarqube_env in env:
            sonarqube = Sonarqube(token=args.sonarqube_auth_token, url=sonarqube_env['url'])
            sonarqube.validate_users_case_insensitive(rw_users + ro_users)
            sonarqube.validate_projects_case_insensitive(projects)
            sonarqube.validate_groups_case_insensitive(rw_groups + ro_groups)
            
            ro_users = sonarqube.get_user_emails_with_correct_case(ro_users)
            rw_users = sonarqube.get_user_emails_with_correct_case(rw_users)
            ro_groups = sonarqube.get_group_names_with_correct_case(ro_groups)
            rw_groups = sonarqube.get_group_names_with_correct_case(rw_groups)
            projects = sonarqube.get_project_names_with_correct_case(projects)

            ro_users = sonarqube.get_user_login_names(ro_users)
            rw_users = sonarqube.get_user_login_names(rw_users)
            ro_groups = sonarqube.get_group_names(ro_groups)
            rw_groups = sonarqube.get_group_names(rw_groups)
            projects = sonarqube.get_project_names(projects)
            
            if ro_users:
                sonarqube.set_user_permission(rw_users,projects,"ro")
            if rw_users:
                sonarqube.set_user_permission(ro_users,projects,"rw")
            if ro_groups:
                sonarqube.set_group_permission(ro_groups,projects,"ro")
            if rw_groups:
                sonarqube.set_group_permission(rw_groups,projects,"rw")
                
    except Exception as e:
        print('Error during set permissions.')
        print(e)
        raise e

def get_parsed_list(string_list: str) -> List[str]:
    if not string_list:
        print('No elements in this list.')
        return []
    string_list = string_list.strip()
    string_list = string_list.replace('\s', ',')
    string_list = string_list.replace(' ', ',')
    split_list = string_list.split(',')
    split_list = [lists.strip() for lists in split_list if lists != '']
    print(f'Parsed list: {split_list}')
    return split_list

if __name__ == "__main__":
    set_permission()
