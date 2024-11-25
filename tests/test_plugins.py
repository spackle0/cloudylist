def test_ec2_plugin(mock_ec2_instances):
    """
    Test the EC2 plugin with mocked instances.
    """
    # Fetch EC2 instances using the mocked client
    response = mock_ec2_instances.describe_instances()

    # Assertions to validate the response
    assert len(response["Reservations"]) == 1
    assert len(response["Reservations"][0]["Instances"]) == 1

    instance = response["Reservations"][0]["Instances"][0]
    assert instance["InstanceType"] == "t2.micro"
    assert instance["ImageId"] == "ami-12345678"


def test_s3_plugin(mock_s3_buckets):
    """
    Test the S3 plugin with mocked buckets.
    """
    # Fetch S3 buckets using the mocked client
    response = mock_s3_buckets.list_buckets()

    # Assertions to validate the response
    assert len(response["Buckets"]) == 1
    assert response["Buckets"][0]["Name"] == "my-test-bucket"


def test_rds_plugin(mock_rds_instances):
    """
    Test the RDS plugin with mocked DB instances.
    """
    # Fetch RDS instances using the mocked client
    response = mock_rds_instances.describe_db_instances()

    # Assertions to validate the response
    assert len(response["DBInstances"]) == 1

    db_instance = response["DBInstances"][0]
    assert db_instance["DBInstanceIdentifier"] == "test-db"
    assert db_instance["DBInstanceClass"] == "db.t2.micro"
    assert db_instance["Engine"] == "mysql"
