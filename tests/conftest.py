import boto3
from moto import mock_aws
import pytest


@pytest.fixture
def mock_ec2_instances():
    """
    Mock EC2 instances using Moto 5's mock_aws.
    """
    with mock_aws():
        ec2_client = boto3.client("ec2", region_name="us-east-1")

        # Create a mock EC2 instance
        ec2_client.run_instances(
            ImageId="ami-12345678",
            MinCount=1,
            MaxCount=1,
            InstanceType="t2.micro",
        )

        yield ec2_client


@pytest.fixture
def mock_s3_buckets():
    """
    Mock S3 buckets using Moto 5's mock_aws.
    """
    with mock_aws():
        s3_client = boto3.client("s3", region_name="us-east-1")

        # Create a mock S3 bucket
        s3_client.create_bucket(Bucket="my-test-bucket")

        yield s3_client


@pytest.fixture
def mock_rds_instances():
    """
    Mock RDS instances using Moto 5's mock_aws.
    """
    with mock_aws():
        rds_client = boto3.client("rds", region_name="us-east-1")

        # Create a mock RDS instance
        rds_client.create_db_instance(
            DBInstanceIdentifier="test-db",
            DBInstanceClass="db.t2.micro",
            Engine="mysql",
            AllocatedStorage=20,
            MasterUsername="admin",
            MasterUserPassword="password",
        )

        yield rds_client
