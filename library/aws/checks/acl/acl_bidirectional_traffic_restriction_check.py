"""
AUTHOR: deepak-puri-comprinno
EMAIL: deepak.puri@comprinno.net
DATE: 2024-11-15
"""

import boto3
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

class acl_bidirectional_traffic_restriction_check(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('ec2')
        report = CheckReport(name=__name__)
        report.resource_ids_status = []
        report.status = CheckStatus.PASSED
        all_nacls = []
        paginator = client.get_paginator('describe_network_acls')
        
        for page in paginator.paginate():
            all_nacls.extend(page['NetworkAcls'])

        for nacl in all_nacls:
            nacl_id = nacl['NetworkAclId']
            is_bidirectional_traffic_restricted = True

            for entry in nacl['Entries']:
                if not entry['Egress'] and entry['RuleAction'] == 'allow':
                    for egress_entry in nacl['Entries']:
                        if egress_entry['Egress'] and egress_entry['RuleAction'] == 'allow' and \
                                entry['CidrBlock'] == egress_entry['CidrBlock']:
                            is_bidirectional_traffic_restricted = False
                            break

            if not is_bidirectional_traffic_restricted:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=nacl_id),
                        status=CheckStatus.FAILED,
                        summary='Bidirectional traffic is not restricted.'
                    )
                )
                report.status = CheckStatus.FAILED
            else:
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=nacl_id),
                        status=CheckStatus.PASSED,
                        summary='Bidirectional traffic is configured properly.'
                    )
                )

        return report

