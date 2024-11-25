from unittest.mock import MagicMock, patch
from cloudylist.utils import collect_inventory
from cloudylist.main import show_inventory


def test_collect_inventory_exceptions():
    """Test exception handling in collect_inventory."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]

    with patch("cloudylist.utils.assume_role", side_effect=Exception("AssumeRoleError")) as mock_assume_role:
        inventory = collect_inventory(mock_config, mock_plugins)
        assert len(inventory) == 0  # Ensure no inventory is collected
        mock_assume_role.assert_called_once_with("123456789012", "TestRole")


def test_collect_inventory_plugin_exception():
    """Test plugin exception handling in collect_inventory."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]
    mock_plugins["ec2"].plugin.side_effect = Exception("PluginError")

    with patch("cloudylist.utils.assume_role", return_value={"AccessKeyId": "key"}):
        inventory = collect_inventory(mock_config, mock_plugins)
        assert len(inventory) == 0  # Ensure no inventory is collected


def test_show_inventory_json():
    """Test show_inventory with JSON output."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]
    mock_plugins["ec2"].plugin.return_value = [{"InstanceId": "i-12345678", "State": "running", "Type": "t2.micro"}]

    with (
        patch("cloudylist.main.load_config", return_value=mock_config),
        patch("cloudylist.main.ExtensionManager", return_value=mock_plugins),
        patch(
            "cloudylist.main.collect_inventory",
            return_value=[
                {
                    "account": "123456789012",
                    "region": "us-east-1",
                    "service": "ec2",
                    "resources": [{"InstanceId": "i-12345678", "State": "running"}],
                }
            ],
        ),
        patch("cloudylist.main.console.print_json") as mock_json_print,
    ):
        show_inventory(config_file="config.yml", format="json")
        mock_json_print.assert_called_once()


def test_show_inventory_yaml():
    """Test show_inventory with YAML output."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]
    mock_plugins["ec2"].plugin.return_value = [{"InstanceId": "i-12345678", "State": "running", "Type": "t2.micro"}]

    with (
        patch("cloudylist.main.load_config", return_value=mock_config),
        patch("cloudylist.main.ExtensionManager", return_value=mock_plugins),
        patch(
            "cloudylist.main.collect_inventory",
            return_value=[
                {
                    "account": "123456789012",
                    "region": "us-east-1",
                    "service": "ec2",
                    "resources": [{"InstanceId": "i-12345678", "State": "running"}],
                }
            ],
        ),
        patch("cloudylist.main.console.print") as mock_yaml_print,
    ):
        show_inventory(config_file="config.yml", format="yaml")
        mock_yaml_print.assert_called()


def test_show_inventory_invalid_format():
    """Test show_inventory with invalid format."""
    with patch("cloudylist.main.console.print") as mock_console:
        show_inventory(config_file="config.yml", format="invalid")
        mock_console.assert_called_once_with("[red]Invalid format:[/red] invalid", style="bold red")


def test_show_inventory_table():
    """Test show_inventory with table output."""
    mock_config = {"accounts": [{"account_id": "123456789012", "role_name": "TestRole"}], "regions": ["us-east-1"]}

    mock_plugins = MagicMock()
    mock_plugins.names.return_value = ["ec2"]
    mock_plugins["ec2"].plugin.return_value = [{"InstanceId": "i-12345678", "State": "running", "Type": "t2.micro"}]

    with (
        patch("cloudylist.main.load_config", return_value=mock_config),
        patch("cloudylist.main.ExtensionManager", return_value=mock_plugins),
        patch(
            "cloudylist.main.collect_inventory",
            return_value=[
                {
                    "account": "123456789012",
                    "region": "us-east-1",
                    "service": "ec2",
                    "resources": [{"InstanceId": "i-12345678", "State": "running"}],
                }
            ],
        ),
        patch("cloudylist.main.console.print") as mock_table_print,
    ):
        show_inventory(config_file="config.yml", format="table")
        mock_table_print.assert_called()
