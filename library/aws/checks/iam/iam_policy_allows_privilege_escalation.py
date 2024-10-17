"""
AUTHOR: Mohd Asif <mohd.asif@comprinno.net>
DATE: 2024-10-10
"""


# import boto3
# from tevico.engine.entities.report.check_model import CheckReport
# from tevico.engine.entities.check.check import Check

# class iam_policy_allows_privilege_escalation(Check):
#     def execute(self, connection: boto3.Session) -> CheckReport:
#         report = CheckReport(name=__name__)
#         client = connection.client('iam')
        
#         # Define privilege escalation actions that we want to check for
#         privilege_escalation_actions = [
#             'iam:CreatePolicy', 'iam:PutUserPolicy', 'iam:PutRolePolicy', 
#             'iam:AttachUserPolicy', 'iam:AttachRolePolicy', 'iam:PassRole',
#             'sts:AssumeRole'
#         ]
        
#         try:
#             # List all IAM users, roles, and groups to check their policies
#             users = client.list_users()['Users']
#             roles = client.list_roles()['Roles']
#             groups = client.list_groups()['Groups']

#             def check_policies(policies):
#                 """Helper function to check policy documents for escalation actions"""
#                 for policy in policies:
#                     policy_arn = policy['PolicyArn']
#                     policy_version = client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
#                     policy_document = client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)['PolicyVersion']['Document']
                    
#                     # Check policy statements for actions that allow privilege escalation
#                     for statement in policy_document.get('Statement', []):
#                         actions = statement.get('Action', [])
#                         if not isinstance(actions, list):
#                             actions = [actions]
                        
#                         for action in actions:
#                             if action in privilege_escalation_actions:
#                                 return True  # Privilege escalation action found
#                 return False

#             # Check users for privilege escalation policies
#             for user in users:
#                 username = user['UserName']
#                 attached_policies = client.list_attached_user_policies(UserName=username)['AttachedPolicies']
#                 inline_policies = client.list_user_policies(UserName=username)['PolicyNames']
                
#                 if check_policies(attached_policies):
#                     # print(f"Privilege escalation policy found for user: {username}")
#                     report.resource_ids_status[username] = True
#                 else:
#                     # print(f"No privilege escalation policy found for user: {username}")
#                     report.resource_ids_status[username] = False

#             # Check roles for privilege escalation policies
#             for role in roles:
#                 role_name = role['RoleName']
#                 attached_policies = client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
#                 inline_policies = client.list_role_policies(RoleName=role_name)['PolicyNames']

#                 if check_policies(attached_policies):
#                     # print(f"Privilege escalation policy found for role: {role_name}")
#                     report.resource_ids_status[role_name] = True
#                 else:
#                     # print(f"No privilege escalation policy found for role: {role_name}")
#                     report.resource_ids_status[role_name] = False

#             # Check groups for privilege escalation policies
#             for group in groups:
#                 group_name = group['GroupName']
#                 attached_policies = client.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']
#                 inline_policies = client.list_group_policies(GroupName=group_name)['PolicyNames']

#                 if check_policies(attached_policies):
#                     # print(f"Privilege escalation policy found for group: {group_name}")
#                     report.resource_ids_status[group_name] = True
#                 else:
#                     # print(f"No privilege escalation policy found for group: {group_name}")
#                     report.resource_ids_status[group_name] = False

#             # Set overall check status
#             report.passed = not any(report.resource_ids_status.values())
        
#         except Exception as e:
#             # print("Error in checking policies for privilege escalation")
#             # print(str(e))
#             report.passed = False
        
#         return report


import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check

class iam_policy_allows_privilege_escalation(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client('iam')

        try:
            # List all IAM users to check their policies
            users = client.list_users()['Users']
            # Define a set of actions that may indicate privilege escalation
            privilege_escalation_actions = set()

            # Get all policies to check for potential privilege escalation actions
            paginator = client.get_paginator('list_policies')
            for page in paginator.paginate(Scope='Local'):
                for policy in page['Policies']:
                    policy_version = client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
                    policy_document = client.get_policy_version(PolicyArn=policy['PolicyArn'], VersionId=policy_version)['PolicyVersion']['Document']
                    
                    # Collect actions from each policy document
                    for statement in policy_document.get('Statement', []):
                        actions = statement.get('Action', [])
                        if not isinstance(actions, list):
                            actions = [actions]
                        
                        privilege_escalation_actions.update(actions)

            def check_policies(policies):
                """Helper function to check policy documents for escalation actions"""
                for policy in policies:
                    policy_arn = policy['PolicyArn']
                    if not is_custom_policy(policy_arn):  # Only check custom policies
                        continue

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
                    report.resource_ids_status[username] = True
                else:
                    report.resource_ids_status[username] = False

            # Set overall check status
            report.passed = not any(report.resource_ids_status.values())
        
        except Exception as e:
            report.passed = False
        
        return report

    def is_custom_policy(self, policy_arn):
        """Check if a policy is custom by examining the ARN"""
        return not policy_arn.startswith('arn:aws:iam::aws:policy/')











































































































# import boto3
# from tevico.engine.entities.report.check_model import CheckReport
# from tevico.engine.entities.check.check import Check

# class iam_policy_allows_privilege_escalation(Check):
#     def execute(self, connection: boto3.Session) -> CheckReport:
#         report = CheckReport(name=__name__)
#         client = connection.client('iam')

#         try:
#             # List all IAM users to check their policies
#             users = client.list_users()['Users']
#             # Define a set of actions that may indicate privilege escalation
#             privilege_escalation_actions = set()
#             custom_policy_names = []  # List to store custom policy ARNs being checked

#             # Get all policies to check for potential privilege escalation actions
#             paginator = client.get_paginator('list_policies')
#             for page in paginator.paginate(Scope='Local'):
#                 for policy in page['Policies']:
#                     # Debugging: Print the entire policy to understand its structure
#                     print("Policy structure:", policy)
#                     if 'PolicyArn' not in policy:
#                         print("PolicyArn key not found in policy:", policy)
#                         continue
                    
#                     policy_version = client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
#                     policy_document = client.get_policy_version(PolicyArn=policy['PolicyArn'], VersionId=policy_version)['PolicyVersion']['Document']
                    
#                     # Collect actions from each policy document
#                     for statement in policy_document.get('Statement', []):
#                         actions = statement.get('Action', [])
#                         if not isinstance(actions, list):
#                             actions = [actions]
                        
#                         privilege_escalation_actions.update(actions)

#             def check_policies(policies):
#                 """Helper function to check policy documents for escalation actions"""
#                 for policy in policies:
#                     policy_arn = policy.get('PolicyArn')  # Use get() to avoid KeyError
#                     if not self.is_custom_policy(policy_arn):  # Only check custom policies
#                         continue

#                     # Add the custom policy ARN to the list
#                     custom_policy_names.append(policy_arn)

#                     # Fetch policy version and document
#                     policy_version = client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
#                     policy_document = client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)['PolicyVersion']['Document']
                    
#                     # Check policy statements for actions that allow privilege escalation
#                     for statement in policy_document.get('Statement', []):
#                         actions = statement.get('Action', [])
#                         if not isinstance(actions, list):
#                             actions = [actions]
                        
#                         for action in actions:
#                             if action in privilege_escalation_actions:
#                                 return True  # Privilege escalation action found
#                 return False

#             # Check users for privilege escalation policies
#             for user in users:
#                 username = user['UserName']
#                 attached_policies = client.list_attached_user_policies(UserName=username)['AttachedPolicies']
#                 inline_policies = client.list_user_policies(UserName=username)['PolicyNames']
                
#                 if check_policies(attached_policies):
#                     report.resource_ids_status[username] = True
#                 else:
#                     report.resource_ids_status[username] = False

#             # Print the list of custom policies checked
#             print("Custom policies checked for privilege escalation:")
#             for policy in custom_policy_names:
#                 print(policy)

#             # Set overall check status
#             report.passed = not any(report.resource_ids_status.values())
        
#         except Exception as e:
#             print(f"An error occurred: {e}")  # Print the exception for debugging
#             report.passed = False
        
#         return report

#     def is_custom_policy(self, policy_arn):
#         """Check if a policy is custom by examining the ARN"""
#         return not policy_arn.startswith('arn:aws:iam::aws:policy/')

