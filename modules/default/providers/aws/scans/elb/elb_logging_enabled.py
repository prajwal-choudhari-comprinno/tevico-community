import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class elb_logging_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        client = connection.client('elb')
        res = client.describe_load_balancers()
        
        load_balancers = res['LoadBalancerDescriptions']
        
        report = ScanReport()
        
        for lb in load_balancers:
            lb_name = lb['LoadBalancerName']

            res = client.describe_load_balancer_attributes(LoadBalancerName=lb_name)
            lb_attributes = res['LoadBalancerAttributes']

            print(f'lb_attributes = {lb_attributes}')

            report.passed = False
            report.resource_ids_status[lb_name] = False

            for attr in lb_attributes['LoadBalancerAttributes']:
                if attr['Key'] == 'access_logs.s3.enabled' and attr['Value'] == 'true':
                    report.passed = True
                    report.resource_ids_status[lb_name] = True

        return report
