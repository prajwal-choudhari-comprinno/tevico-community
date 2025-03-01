import boto3

from typing import Any
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class opensearch_service_domains_audit_logging_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('opensearch')
        res = client.list_domain_names()
        
        domain_names = res['DomainNames']
        
        report = CheckReport(name=__name__)
        report.status = CheckStatus.FAILED
        
        for dn in domain_names:
            domain_name = dn['DomainName']
            res = client.describe_domain(DomainName=domain_name)
            domain = res['DomainStatus']
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name=domain_name),
                    status=CheckStatus.FAILED,
                    summary=''
                )
            )
            if domain['LogPublishingOptions']['Options']['AUDIT_LOGS']['Enabled']:
                report.status = CheckStatus.PASSED
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=domain_name),
                        status=CheckStatus.PASSED,
                        summary=''
                    )
                )

        return report
    
