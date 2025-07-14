import pytest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError
from tevico.engine.entities.report.check_model import (
    CheckStatus,
    CheckMetadata,
    Remediation,
    RemediationCode,
    RemediationRecommendation,
)
from library.aws.checks.apigateway.apigateway_rest_api_waf_acl_attached import (
    apigateway_rest_api_waf_acl_attached,
)

class TestApiGatewayRestApiWafAclAttached:
    """Test cases for API Gateway REST API WAF ACL Attached check."""

    def setup_method(self):
        self.metadata = CheckMetadata(
            Provider="AWS",
            CheckID="apigateway_rest_api_waf_acl_attached",
            CheckTitle="API Gateway REST API has WAF ACL attached",
            CheckType=["Security"],
            ServiceName="APIGateway",
            SubServiceName="REST API",
            ResourceIdTemplate="arn:aws:apigateway:{region}::/restapis/{restapi_id}",
            Severity="medium",
            ResourceType="AWS::ApiGateway::RestApi",
            Risk="APIs without WAF ACL may be vulnerable to web attacks.",
            Description="Checks if API Gateway REST APIs have a WAF ACL attached.",
            Remediation=Remediation(
                Code=RemediationCode(CLI="", NativeIaC="", Terraform=""),
                Recommendation=RemediationRecommendation(
                    Text="Attach a WAF ACL to API Gateway REST APIs.",
                    Url="https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-control-access-to-api.html"
                )
            )
        )
        self.check = apigateway_rest_api_waf_acl_attached(metadata=self.metadata)
        self.mock_session = MagicMock()
        self.mock_apigw = MagicMock()
        self.mock_session.client.return_value = self.mock_apigw
        self.mock_session.region_name = "us-west-2"

    def test_no_rest_apis(self):
        """Test when there are no REST APIs."""
        self.mock_apigw.get_rest_apis.return_value = {"items": []}

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.PASSED
        assert len(report.resource_ids_status) == 0

    def test_waf_acl_attached(self):
        """Test when a REST API has WAF ACL attached to all stages."""
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-1", "name": "API 1"}]
        }
        self.mock_apigw.get_stages.return_value = {
            "item": [
                {
                    "stageName": "prod",
                    "webAclArn": "arn:aws:wafv2:us-west-2:123456789012:regional/webacl/sample"
                }
            ]
        }

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.PASSED
        assert len(report.resource_ids_status) == 1
        assert report.resource_ids_status[0].status == CheckStatus.PASSED
        assert "WAF is attached to stage prod of API API 1." in report.resource_ids_status[0].summary

    def test_waf_acl_not_attached(self):
        """Test when a REST API stage does not have WAF ACL attached."""
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-2", "name": "API 2"}]
        }
        self.mock_apigw.get_stages.return_value = {
            "item": [
                {
                    "stageName": "dev"
                    # no webAclArn
                }
            ]
        }

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.FAILED
        assert len(report.resource_ids_status) == 1
        assert report.resource_ids_status[0].status == CheckStatus.FAILED
        assert "No WAF attached to stage dev of API API 2." in report.resource_ids_status[0].summary

    def test_api_with_no_stages(self):
        """Test when API has no stages."""
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-3", "name": "API 3"}]
        }
        self.mock_apigw.get_stages.return_value = {
            "item": []
        }

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.FAILED
        assert len(report.resource_ids_status) == 1
        assert report.resource_ids_status[0].status == CheckStatus.FAILED
        assert "API API 3 has no stages." in report.resource_ids_status[0].summary

    def test_get_stages_exception(self):
        """Test when exception occurs while getting stages."""
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-4", "name": "API 4"}]
        }
        self.mock_apigw.get_stages.side_effect = Exception("stage error")

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.UNKNOWN
        assert report.resource_ids_status[0].status == CheckStatus.UNKNOWN
        assert "Error fetching stages for API API 4." in report.resource_ids_status[0].summary

    def test_get_rest_apis_exception(self):
        """Test when exception occurs while listing REST APIs."""
        self.mock_apigw.get_rest_apis.side_effect = ClientError(
            {"Error": {"Code": "AccessDeniedException", "Message": "Access denied"}},
            "GetRestApis"
        )

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.UNKNOWN
        assert report.resource_ids_status[0].status == CheckStatus.UNKNOWN
        assert "API Gateway listing error occurred." in report.resource_ids_status[0].summary
