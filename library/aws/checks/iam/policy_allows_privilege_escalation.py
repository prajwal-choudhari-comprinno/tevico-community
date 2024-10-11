"""
AUTHOR: Mohd Asif
DATE: 11 oct 2024
"""


import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class policy_allows_privilege_escalation(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')
        
        # Define privilege escalation actions that we want to check for
        privilege_escalation_actions = [
            'iam:CreatePolicy', 'iam:PutUserPolicy', 'iam:PutRolePolicy', 
            'iam:AttachUserPolicy', 'iam:AttachRolePolicy', 'iam:PassRole',
            'sts:AssumeRole'
        ]
        
        try:
            # List all IAM users, roles, and groups to check their policies
            users = client.list_users()['Users']
            roles = client.list_roles()['Roles']
            groups = client.list_groups()['Groups']

            def check_policies(policies):
                """Helper function to check policy documents for escalation actions"""
                for policy in policies:
                    policy_arn = policy['PolicyArn']
                    policy_version = client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
                    policy_document = client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)['PolicyVersion']['Document']
                    
                    # Check policy statements for actions that allow privilege escalation
                    for statement in policy_document.get('Statement', []):
                        actions = statement.get('Action', [])
                        if not isinstance(actions, list):
                            actions = [actions]
                        
                        for action in actions:
                            if action in privilege_escalation_actions:
                                return True  # Privilege escalation action found
                return False

            # Check users for privilege escalation policies
            for user in users:
                username = user['UserName']
                attached_policies = client.list_attached_user_policies(UserName=username)['AttachedPolicies']
                inline_policies = client.list_user_policies(UserName=username)['PolicyNames']
                
                if check_policies(attached_policies):
                    print(f"Privilege escalation policy found for user: {username}")
                    report.resource_ids_status[username] = True
                else:
                    print(f"No privilege escalation policy found for user: {username}")
                    report.resource_ids_status[username] = False

            # Check roles for privilege escalation policies
            for role in roles:
                role_name = role['RoleName']
                attached_policies = client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
                inline_policies = client.list_role_policies(RoleName=role_name)['PolicyNames']

                if check_policies(attached_policies):
                    print(f"Privilege escalation policy found for role: {role_name}")
                    report.resource_ids_status[role_name] = True
                else:
                    print(f"No privilege escalation policy found for role: {role_name}")
                    report.resource_ids_status[role_name] = False

            # Check groups for privilege escalation policies
            for group in groups:
                group_name = group['GroupName']
                attached_policies = client.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']
                inline_policies = client.list_group_policies(GroupName=group_name)['PolicyNames']

                if check_policies(attached_policies):
                    print(f"Privilege escalation policy found for group: {group_name}")
                    report.resource_ids_status[group_name] = True
                else:
                    print(f"No privilege escalation policy found for group: {group_name}")
                    report.resource_ids_status[group_name] = False

            # Set overall check status
            report.passed = not any(report.resource_ids_status.values())
        
        except Exception as e:
            print("Error in checking policies for privilege escalation")
            print(str(e))
            report.passed = False
        
        return report
