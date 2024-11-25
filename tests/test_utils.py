from cloudylist.utils import assume_role


def test_assume_role(mocker):
    """
    Test assume_role by explicitly mocking boto3.client.
    """
    # Mock the AWS STS client and its assume_role method
    mock_sts_client = mocker.Mock()
    mock_sts_client.assume_role.return_value = {
        "Credentials": {
            "AccessKeyId": "mock-access-key",
            "SecretAccessKey": "mock-secret-key",
            "SessionToken": "mock-session-token",
        }
    }

    # Patch boto3.client to return the mocked STS client
    mocker.patch("boto3.client", return_value=mock_sts_client)

    # Call the assume_role function
    credentials = assume_role("123456789012", "TestRole")

    # Validate that assume_role was called correctly
    mock_sts_client.assume_role.assert_called_once_with(
        RoleArn="arn:aws:iam::123456789012:role/TestRole",
        RoleSessionName="MultiAccountInventorySession",  # Match the actual implementation
    )

    # Validate the returned credentials
    assert credentials["AccessKeyId"] == "mock-access-key"
    assert credentials["SecretAccessKey"] == "mock-secret-key"
    assert credentials["SessionToken"] == "mock-session-token"
