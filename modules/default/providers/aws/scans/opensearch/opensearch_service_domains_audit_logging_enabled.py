import boto3

from typing import Any
from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class opensearch_service_domains_audit_logging_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        client = connection.client('opensearch')
        res = client.list_domain_names()
        
        domain_names = res['DomainNames']
        
        report = ScanReport()
        
        for dn in domain_names:
            domain_name = dn['DomainName']
            res = client.describe_domain(DomainName=domain_name)
            domain = res['DomainStatus']
            report.passed = False
            report.resource_ids_status[domain_name] = False
            if domain['LogPublishingOptions']['Options']['AUDIT_LOGS']['Enabled']:
                report.passed = True
                report.resource_ids_status[domain_name] = True

        return report
    
