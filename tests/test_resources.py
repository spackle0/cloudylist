import pytest
from unittest.mock import MagicMock
from moto import mock_aws
import boto3
from cloudylist.resources.ec2 import list_resources as list_ec2_resources
from cloudylist.resources.s3 import list_resources as list_s3_resources
from cloudylist.resources.rds import list_resources as list_rds_resources

@pytest.fixture
def mock_ec2_client():
    """Mock EC2 client with moto."""
    with mock_aws():
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        # Add mock data
        ec2_client.describe_instances = MagicMock(
            return_value={
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-12345678",
                                "State": {"Name": "running"},
                                "InstanceType": "t2.micro",
                            }
                        ]
                    }
                ]
            }
        )
        yield ec2_client

@pytest.fixture
def mock_s3_client():
    """Mock S3 client with moto."""
    with mock_aws():
        s3_client = boto3.client("s3", region_name="us-east-1")
        # Add mock data
        s3_client.list_buckets = MagicMock(
            return_value={
                "Buckets": [
                    {"Name": "my-bucket", "CreationDate": "2024-01-01T00:00:00Z"}
                ]
            }
        )
        yield s3_client

@pytest.fixture
def mock_rds_client():
    """Mock RDS client with moto."""
    with mock_aws():
        rds_client = boto3.client("rds", region_name="us-east-1")
        # Add mock data
        rds_client.describe_db_instances = MagicMock(
            return_value={
                "DBInstances": [
                    {
                        "DBInstanceIdentifier": "test-db",
                        "DBInstanceStatus": "available",
                        "DBInstanceClass": "db.t2.micro",
                    }
                ]
            }
        )
        yield rds_client

def test_list_resources_ec2(mock_ec2_client):
    """Test EC2 list_resources."""
    result = list_ec2_resources(mock_ec2_client)
    assert len(result) == 1
    assert result[0]['InstanceId'] == 'i-12345678'
    assert result[0]['State'] == 'running'
    assert result[0]['Type'] == 't2.micro'

def test_list_resources_s3(mock_s3_client):
    """Test S3 list_resources."""
    result = list_s3_resources(mock_s3_client)
    print(result)
    assert len(result) == 1
    assert result[0]["Name"] == "my-bucket"
    assert result[0]["CreationDate"] == "2024-01-01T00:00:00Z"

def test_list_resources_rds(mock_rds_client):
    """Test RDS list_resources."""
    result = list_rds_resources(mock_rds_client)
    print(result)
    assert len(result) == 1
    assert result[0]['DBInstanceIdentifier'] == 'test-db'
    assert result[0]['Status'] == 'available'
