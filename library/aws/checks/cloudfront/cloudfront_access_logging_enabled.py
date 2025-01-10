import boto3
import logging

from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check


class cloudfront_access_logging_enabled(Check):
    def execute(self, connection: boto3.Session) -> CheckReport:
        # Initialize CloudFront client and report
        client = connection.client('cloudfront')
        report = CheckReport(name=__name__)
        report.passed = True
        report.resource_ids_status = {}

        try:
            # List all distributions
            distributions = []
            next_marker = None

            while True:
                response = client.list_distributions(Marker=next_marker) if next_marker else client.list_distributions()
                distributions.extend(response.get('DistributionList', {}).get('Items', []))
                next_marker = response.get('NextMarker')
                if not next_marker:
                    break

            # Get and log the configuration of each distribution
            for distribution in distributions:
                distribution_id = distribution['Id']

                # Get the distribution configuration using get_distribution_config
                dist_config = client.get_distribution_config(Id=distribution_id)

                # For example, you can check if logging is enabled
                logging_config = dist_config.get('DistributionConfig', {}).get('Logging', {})
                logging_enabled = logging_config.get('Enabled', False)

                # Log the result
                status = logging_enabled
                report.resource_ids_status[f"{distribution_id} Access Logging: {'Enabled' if status else 'Disabled'}"] = status

                if not status:
                    report.passed = False  # Mark as failed if any distribution does not have logging enabled

        except Exception as e:
            logging.error(f"Error while fetching CloudFront distribution config: {e}")
            report.passed = False
            report.resource_ids_status = {}

        return report
