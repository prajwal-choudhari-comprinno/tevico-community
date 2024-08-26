import boto3

from tevico.framework.entities.report.scan_model import ScanReport
from tevico.framework.entities.scan.scan import Scan


class apigateway_restapi_logging_enabled(Scan):

    def execute(self, connection: boto3.Session) -> ScanReport:
        report = ScanReport(name=__name__)
        client = connection.client('apigateway')
        apis = client.get_rest_apis()['items']
        for api in apis:
            api_name = api['name']
            logging = api['endpointConfiguration']['types']
            if 'REGIONAL' in logging:
                report.passed = True
                report.resource_ids_status[api_name] = True
            else:
                report.passed = False
                report.resource_ids_status[api_name] = False
        return report

