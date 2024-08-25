import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class opensearch_service_domains_cloudwatch_logging_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        client = connection.client('opensearch')
        res = client.list_domain_names()
        
        domain_names = res['DomainNames']
        
        report = ScanReport()
        
        log_publishing_options = [
            'INDEX_SLOW_LOGS',
            'SEARCH_SLOW_LOGS',
            'ES_APPLICATION_LOGS'
        ]
        
        for dn in domain_names:
            domain_name = dn['DomainName']
            res = client.describe_domain_config(DomainName=domain_name)
            for log_option in log_publishing_options:
                report.passed = False
                report.resource_ids_status[domain_name] = False
                if res['DomainConfig']['LogPublishingOptions'][log_option]['Enabled']:
                    report.passed = True
                    report.resource_ids_status[domain_name] = True

        return report
        
