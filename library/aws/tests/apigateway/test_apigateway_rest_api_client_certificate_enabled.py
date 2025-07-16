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
from library.aws.checks.apigateway.apigateway_rest_api_client_certificate_enabled import (
    apigateway_rest_api_client_certificate_enabled,
)


class TestApiGatewayRestApiClientCertificateEnabled:
    """Tests for apigateway_rest_api_client_certificate_enabled check."""

    def setup_method(self):
        self.metadata = CheckMetadata(
            Provider="AWS",
            CheckID="apigateway_rest_api_client_certificate_enabled",
            CheckTitle="API Gateway REST API stages have client certificate enabled",
            CheckType=["Security"],
            ServiceName="APIGateway",
            SubServiceName="REST API",
            ResourceIdTemplate="arn:aws:apigateway:{region}::/restapis/{restapi_id}",
            Severity="medium",
            ResourceType="AWS::ApiGateway::RestApi",
            Risk="APIs without client certificate may lack mutual TLS authentication.",
            Description="Checks if API Gateway REST API stages have client certificate enabled.",
            Remediation=Remediation(
                Code=RemediationCode(CLI="", NativeIaC="", Terraform=""),
                Recommendation=RemediationRecommendation(
                    Text="Enable client certificate for API Gateway REST API stages.",
                    Url="https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-client-certificate.html"
                )
            )
        )
        self.check = apigateway_rest_api_client_certificate_enabled(metadata=self.metadata)
        self.mock_session = MagicMock()
        self.mock_apigw = MagicMock()
        self.mock_session.client.return_value = self.mock_apigw
        self.mock_session.region_name = "us-west-2"

    def test_all_stages_have_client_certificate(self):
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-1", "name": "API 1"}]
        }
        self.mock_apigw.get_stages.return_value = {
            "item": [{"stageName": "prod", "clientCertificateId": "cert-123"}]
        }

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.PASSED
        assert len(report.resource_ids_status) == 1
        assert report.resource_ids_status[0].status == CheckStatus.PASSED
        assert report.resource_ids_status[0].summary == "Stage prod of API API 1 has a client certificate enabled."

    def test_stage_without_client_certificate(self):
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-2", "name": "API 2"}]
        }
        self.mock_apigw.get_stages.return_value = {
            "item": [{"stageName": "prod"}]
        }

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.FAILED
        assert len(report.resource_ids_status) == 1
        assert report.resource_ids_status[0].status == CheckStatus.FAILED
        assert report.resource_ids_status[0].summary == "Stage prod of API API 2 does not have a client certificate enabled."

    def test_mixed_stages_cert_and_no_cert(self):
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-3", "name": "API 3"}]
        }
        self.mock_apigw.get_stages.return_value = {
            "item": [
                {"stageName": "prod", "clientCertificateId": "cert-123"},
                {"stageName": "dev"}
            ]
        }

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.FAILED
        assert len(report.resource_ids_status) == 2
        summaries = [r.summary for r in report.resource_ids_status]
        assert "Stage prod of API API 3 has a client certificate enabled." in summaries

    def test_no_stages_for_api(self):
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-4", "name": "API 4"}]
        }
        self.mock_apigw.get_stages.return_value = {"item": []}

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.PASSED
        assert len(report.resource_ids_status) == 0

    def test_client_error_on_get_stages(self):
        self.mock_apigw.get_rest_apis.return_value = {
            "items": [{"id": "api-5", "name": "API 5"}]
        }
        self.mock_apigw.get_stages.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}, "GetStages"
        )

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.UNKNOWN
        assert len(report.resource_ids_status) == 1
        assert report.resource_ids_status[0].status == CheckStatus.UNKNOWN
        assert report.resource_ids_status[0].summary == "Error fetching stages for API API 5."
        assert report.resource_ids_status[0].exception is not None
        assert "AccessDenied" in report.resource_ids_status[0].exception

    def test_client_error_on_get_rest_apis(self):
        self.mock_apigw.get_rest_apis.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}, "GetRestApis"
        )

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.UNKNOWN
        assert len(report.resource_ids_status) == 1
        assert report.resource_ids_status[0].status == CheckStatus.UNKNOWN
        assert report.resource_ids_status[0].summary == "API Gateway listing error."
        assert report.resource_ids_status[0].exception is not None
        assert "AccessDenied" in report.resource_ids_status[0].exception

    def test_paginated_rest_apis(self):
        self.mock_apigw.get_rest_apis.side_effect = [
            {"items": [{"id": "api-6a", "name": "API 6a"}], "position": "token-1"},
            {"items": [{"id": "api-6b", "name": "API 6b"}]}
        ]

        self.mock_apigw.get_stages.return_value = {
            "item": [{"stageName": "prod", "clientCertificateId": "cert-123"}]
        }

        report = self.check.execute(self.mock_session)

        assert report.status == CheckStatus.PASSED
        assert len(report.resource_ids_status) == 2
        for r in report.resource_ids_status:
            assert r.status == CheckStatus.PASSED
