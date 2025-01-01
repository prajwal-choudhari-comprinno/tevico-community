from typing import Any, Dict, List
import pytest
import os
import boto3
from library.aws.provider import AWSProvider
from tevico.engine.configs.config import ConfigUtils
from tevico.engine.entities.provider.provider import Provider, CheckReport

class MyProvider(Provider):
    """Provider class for AWS."""

    @property
    def name(self) -> str:
        """Returns the name of the provider.

        Returns:
            str: The name of the provider.
        """
        return "AWS"

    @property
    def metadata(self) -> Dict[str, str]:
        """Returns metadata for the provider.

        Returns:
            Dict[str, str]: Metadata dictionary.
        """
        return {}

    def connect(self) -> Any:
        """Establishes a connection using AWS configuration.

        Returns:
            Any: A boto3 session object.
        """
        aws_config = ConfigUtils().get_config().aws_config

        if aws_config is not None:
            return boto3.Session(profile_name=aws_config['profile'])
        
        return boto3.Session()

def get_check_reports() -> List[CheckReport]:
    """Fetches check reports by executing the provider.

    Returns:
        List[CheckReport]: A list of check reports.
    """
    provider_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../library/aws'))
    provider = MyProvider(path=provider_path)
    return provider.start_execution()

# Get the check reports
check_reports = get_check_reports()

@pytest.mark.parametrize("report", check_reports)
def test_check_report(report: CheckReport):
    """Tests the check report to ensure consistency of resource IDs status.

    Args:
        report (CheckReport): The check report to be tested.
    """
    if any(value is False for value in report.resource_ids_status.values()):
        assert report.passed is False
    else:
        assert report.passed is True