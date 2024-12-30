"""
AUTHOR: RONIT CHAUHAN
DATE: 2024-12-24

Description: This module checks if logging is enabled for ELBv2 Load Balancers (Application, Network, Gateway) 
across all regions or specific region.

What this code does:
1. Finds all modern Load Balancers (ALB, NLB, GWLB) in AWS regions
2. Checks if each load balancer has logging enabled
3. Verifies if logs are being saved to an S3 bucket
4. Reports which load balancers are compliant with logging requirements
"""
import boto3
from tevico.engine.entities.report.check_model import CheckReport
from tevico.engine.entities.check.check import Check
import logging
from botocore.exceptions import (
    ClientError,            # For AWS service-specific errors
    EndpointConnectionError,  # For network connectivity issues
    NoCredentialsError,     # For missing AWS credentials
    InvalidRegionError      # For invalid AWS region specifications
)

# Setup logging to track errors and warnings
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class elb_v2_logging_enabled(Check):
    """
    Security check that verifies if modern Load Balancers have access logging enabled.
    
    Types of Load Balancers checked:
    1. Application Load Balancer (ALB) - for HTTP/HTTPS traffic
    2. Network Load Balancer (NLB) - for TCP/UDP traffic
    3. Gateway Load Balancer (GWLB) - for network security
    """
    # region = ["ap-south-1"]  # Default: Check Mumbai region only
    region = ""           # Alternative: Check all regions

    def get_all_regions(self, connection: boto3.Session):
        """
        Gets the list of AWS regions to check based on configuration.

        How it works:
        1. Uses configured regions if specified
        2. Otherwise, gets a list of all AWS regions
        3. Handles various error cases with clear messages
        """
        try:
            # Check if specific regions are configured
            if self.region:
                return self.region if isinstance(self.region, list) else [self.region]
            
            # If no regions specified, get all AWS regions
            ec2 = connection.client('ec2', region_name='us-east-1')
            regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
            return regions

        except NoCredentialsError:
            # Handle missing AWS credentials
            logger.error("🔑 Error: AWS credentials not found. Please configure your AWS credentials.")
            return []
        except ClientError as e:
            # Handle AWS API errors
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"⚠️ AWS API Error ({error_code}): {error_message}")
            return []
        except InvalidRegionError:
            # Handle invalid region specifications
            logger.error("🌎 Error: Invalid AWS region specified")
            return []
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"❌ Unexpected error while getting regions: {str(e)}")
            return []

    def check_elbv2_logging(self, client, lb_arn, lb_name):
        """
        Checks if a modern Load Balancer has logging properly configured.

        What it checks:
        1. If access logging is enabled
        2. If an S3 bucket is configured for storing logs

        Returns:
        - is_compliant: True if logging is properly configured
        - s3_bucket: Name of the bucket where logs are stored
        """
        try:
            # Get load balancer settings
            attrs = client.describe_load_balancer_attributes(LoadBalancerArn=lb_arn)
            
            logging_enabled = False
            s3_bucket = None
            
            # Check each setting
            for attr in attrs['Attributes']:
                if attr['Key'] == 'access_logs.s3.enabled':
                    logging_enabled = (attr['Value'].lower() == 'true')
                elif attr['Key'] == 'access_logs.s3.bucket':
                    s3_bucket = attr['Value']
            
            # Both logging must be enabled and S3 bucket must be configured
            return logging_enabled and bool(s3_bucket), s3_bucket

        except ClientError as e:
            # Handle AWS-specific errors
            error_code = e.response['Error']['Code']
            if error_code == 'LoadBalancerNotFound':
                logger.error(f"🔍 Load balancer '{lb_name}' not found")
            else:
                logger.error(f"⚠️ AWS API error checking '{lb_name}': {e.response['Error']['Message']}")
            return False, None
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"❌ Error checking ELBv2 '{lb_name}': {str(e)}")
            return False, None

    def execute(self, connection: boto3.Session) -> CheckReport:
        """
        Main method that checks all modern Load Balancers.

        Process:
        1. Gets list of regions to check
        2. For each region:
           - Finds all modern Load Balancers
           - Checks if logging is properly configured
           - Records results
        3. Creates final report showing which load balancers pass or fail

        Returns:
        - Report showing compliance status of all load balancers
        """
        # Initialize the report
        report = CheckReport(name=__name__)
        report.passed = True  # Start assuming everything passes
        report.resource_ids_status = {}
        found_load_balancers = False

        try:
            # Step 1: Get regions to check
            regions = self.get_all_regions(connection)
            if not regions:
                report.passed = False
                report.resource_ids_status["No Regions Found"] = False
                return report

            # Step 2: Check each region
            for region in regions:
                try:
                    # Create AWS client for this region
                    elbv2_client = connection.client('elbv2', region_name=region)
                    
                    try:
                        # Get all load balancers in this region
                        v2_lbs = elbv2_client.describe_load_balancers()['LoadBalancers']
                        if v2_lbs:
                            found_load_balancers = True
                            
                            # Check each load balancer
                            for lb in v2_lbs:
                                lb_name = lb['LoadBalancerName']
                                lb_arn = lb['LoadBalancerArn']
                                lb_type = lb['Type']  # Will be 'application', 'network', or 'gateway'
                                
                                # Check if logging is properly configured
                                is_compliant, s3_bucket = self.check_elbv2_logging(
                                    elbv2_client, lb_arn, lb_name
                                )
                                
                                # Record the results
                                resource_key = f"{lb_type}:{region}:{lb_name}"
                                report.resource_ids_status[resource_key] = is_compliant
                                
                                # Update overall status if this load balancer fails
                                if not is_compliant:
                                    report.passed = False
                                    logger.warning(f"🚫 Load balancer '{lb_name}' does not have proper logging configured")

                    except ClientError as e:
                        # Handle AWS API errors
                        if e.response['Error']['Code'] != 'AccessDenied':
                            logger.error(f"⚠️ Error checking Load Balancers in {region}: {e.response['Error']['Message']}")

                except EndpointConnectionError:
                    # Handle AWS connectivity issues
                    logger.error(f"🌐 Cannot connect to AWS in region {region}. Check your network connection.")
                    continue
                except Exception as e:
                    # Handle unexpected errors
                    logger.error(f"❌ Unexpected error in region {region}: {str(e)}")
                    continue

            # Step 3: Handle case where no load balancers were found
            if not found_load_balancers:
                report.passed = False
                report.resource_ids_status["No Load Balancers Found"] = False
                logger.warning("ℹ️ No Load Balancers found in any checked region")

        except NoCredentialsError:
            # Handle missing AWS credentials
            logger.error("🔑 AWS credentials not found. Please check your AWS configuration.")
            report.passed = False
            report.resource_ids_status["No AWS Credentials"] = False
        except Exception as e:
            # Handle any other unexpected errors
            logger.error(f"❌ Critical error in check execution: {str(e)}")
            report.passed = False
            report.resource_ids_status["Error"] = False

        return report
