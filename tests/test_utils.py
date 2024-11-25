import logging
from cloudylist.utils import get_logger, collect_inventory, assume_role
from unittest.mock import patch, MagicMock


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


def test_get_logger():
    """Test logger initialization."""
    logger = get_logger("test_logger")
    assert logger is not None
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0


def test_collect_inventory_plugin_error():
    """Test collect_inventory handles plugin errors."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]
    mock_plugins["ec2"].plugin.side_effect = Exception("PluginError")

    with (
        patch("cloudylist.utils.assume_role", return_value={"AccessKeyId": "key"}),
        patch("cloudylist.utils.get_boto3_client"),
    ):
        inventory = collect_inventory(mock_config, mock_plugins)

    # Assert no inventory is collected due to plugin error
    assert len(inventory) == 0


def test_collect_inventory_plugin_exception():
    """Test exception handling for plugins in collect_inventory."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]
    mock_plugins["ec2"].plugin.side_effect = Exception("PluginError")

    with patch("cloudylist.utils.assume_role", return_value={"AccessKeyId": "key"}):
        inventory = collect_inventory(mock_config, mock_plugins)
        assert len(inventory) == 0  # No inventory should be collected due to plugin error


def test_get_logger_initialization():
    """Test logger initialization and handler setup."""
    # Ensure the logger is initialized without handlers
    logger_name = "test_logger"
    test_logger = get_logger(logger_name)
    assert test_logger.name == logger_name
    assert len(test_logger.handlers) > 0


def test_collect_inventory_success():
    """Test that collect_inventory successfully appends to inventory."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]
    mock_plugins["ec2"].plugin.return_value = [{"id": "resource-1"}]

    with (
        patch(
            "cloudylist.utils.assume_role",
            return_value={
                "AccessKeyId": "mock-access-key",
                "SecretAccessKey": "mock-secret-key",
                "SessionToken": "mock-session-token",
            },
        ),
        patch("cloudylist.utils.get_boto3_client"),
    ):
        inventory = collect_inventory(mock_config, mock_plugins)

    # Assert inventory is populated
    assert len(inventory) == 1
    assert inventory[0]["account"] == "123456789012"
    assert inventory[0]["region"] == "us-east-1"
    assert inventory[0]["service"] == "ec2"
    assert inventory[0]["resources"] == [{"id": "resource-1"}]

def test_assume_role_exception(mocker):
    """Test exception handling in assume_role."""
    mocker.patch("cloudylist.utils.boto3.client", side_effect=Exception("Simulated error"))
    config = {
        "accounts": [{"account_id": "123456789012", "role_name": "TestRole"}],
        "regions": ["us-east-1"],
    }
    plugins = mocker.Mock(names=lambda: ["ec2"])

    inventory = collect_inventory(config, plugins)

    assert inventory == []  # No inventory should be collected
