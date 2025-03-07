import logging
import boto3
from datetime import datetime, timezone
from botocore.exceptions import BotoCoreError, ClientError
from tevico.engine.entities.report.check_model import CheckReport, CheckStatus, GeneralResource, ResourceStatus
from tevico.engine.entities.check.check import Check

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define maximum number of days allowed for root access
MAXIMUM_ACCESS_DAYS = 7

# Helper function to parse timestamp safely
def parse_timestamp(timestamp: str):
    """Parses a timestamp string safely and returns a datetime object or None."""
    if timestamp and timestamp not in ["no_information", "not_supported", "N/A"]:
        try:
            return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            logger.warning(f"Unexpected timestamp format: {timestamp}")
    return None

class iam_avoid_root_usage(Check):

    def execute(self, connection: boto3.Session) -> CheckReport:
        report = CheckReport(name=__name__)
        client = connection.client("iam")
        report.resource_ids_status = []

        try:
            logger.info("Generating IAM credential report...")
            client.generate_credential_report()
            response = client.get_credential_report()
            decoded_report = response["Content"].decode("utf-8").splitlines()

            for row in decoded_report[1:]:
                user_info = row.split(",")

                if user_info[0] == "<root_account>":
                    logger.info("Checking root account last access times...")

                    password_last_used = parse_timestamp(user_info[4])
                    access_key_1_last_used = parse_timestamp(user_info[6])
                    access_key_2_last_used = parse_timestamp(user_info[9])

                    last_accessed = max(
                        filter(None, [password_last_used, access_key_1_last_used, access_key_2_last_used]),
                        default=None
                    )

                    if last_accessed:
                        days_since_accessed = (datetime.now(timezone.utc) - last_accessed).days

                        if days_since_accessed <= MAXIMUM_ACCESS_DAYS:
                            logger.warning("Root account has been accessed recently!")
                            report.status = CheckStatus.FAILED
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=GeneralResource(name="Root Account"),
                                    status=CheckStatus.FAILED,
                                    summary="Root account was accessed within the last day. Immediate action required!"
                                )
                            )
                        else:
                            logger.info(f"Root account was last accessed {days_since_accessed} days ago.")
                            report.status = CheckStatus.PASSED
                            report.resource_ids_status.append(
                                ResourceStatus(
                                    resource=GeneralResource(name="Root Account"),
                                    status=CheckStatus.PASSED,
                                    summary=f"Root account last accessed {days_since_accessed} days ago."
                                )
                            )
                    else:
                        logger.info("Root account has not been accessed recently.")
                        report.status = CheckStatus.PASSED
                        report.resource_ids_status.append(
                            ResourceStatus(
                                resource=GeneralResource(name="Root Account"),
                                status=CheckStatus.PASSED,
                                summary="Root account has not been accessed recently."
                            )
                        )

                    break  # Stop after processing root account

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Error retrieving IAM credential report: {str(e)}")
            report.status = CheckStatus.ERRORED
            report.resource_ids_status.append(
                ResourceStatus(
                    resource=GeneralResource(name="Root Account"),
                    status=CheckStatus.ERRORED,
                    summary="Error processing IAM root usage check.",
                    exception=str(e)
                )
            )

        return report
