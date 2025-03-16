import boto3

from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check


class opensearch_service_domains_cloudwatch_logging_enabled(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        client = connection.client('opensearch')
        res = client.list_domain_names()
        
        domain_names = res['DomainNames']
        
        report = CheckReport(name=__name__)
        report.status = CheckStatus.FAILED
        
        log_publishing_options = [
            'INDEX_SLOW_LOGS',
            'SEARCH_SLOW_LOGS',
            'ES_APPLICATION_LOGS'
        ]
        
        for dn in domain_names:
            domain_name = dn['DomainName']
            res = client.describe_domain_config(DomainName=domain_name)
            for log_option in log_publishing_options:
                
                report.resource_ids_status.append(
                    ResourceStatus(
                        resource=GeneralResource(name=domain_name),
                        status=CheckStatus.FAILED,
                        summary=''
                    )
                )
                if res['DomainConfig']['LogPublishingOptions'][log_option]['Enabled']:
                    report.status = CheckStatus.PASSED
                    report.resource_ids_status.append(
                        ResourceStatus(
                            resource=GeneralResource(name=domain_name),
                            status=CheckStatus.PASSED,
                            summary=''
                        )
                    )

        return report
        
