from typing import Any, Dict, List
import pytest
import os
import boto3
from library.aws.provider import AWSProvider
from tevico.engine.configs.config import ConfigUtils
from tevico.engine.entities.provider.provider import CheckReport

def get_check_reports() -> List[CheckReport]:
    """Fetches check reports by executing the provider.

    Returns:
        List[CheckReport]: A list of check reports.
    """
    provider = AWSProvider()
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