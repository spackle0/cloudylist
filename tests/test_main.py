from cloudylist.main import collect_inventory, output_table, output_json, output_yaml
import json
import yaml


def test_collect_inventory(mocker):
    """
    Test the collect_inventory function with mocked plugins and AWS clients, including error handling.
    """
    # Mock AWS client responses
    ec2_mock_response = [{"InstanceId": "i-123abc", "State": "running"}]
    s3_mock_response = [{"Name": "my-bucket", "CreationDate": "2024-01-01T00:00:00Z"}]
    rds_mock_response = [{"DBInstanceIdentifier": "test-db", "DBInstanceStatus": "available"}]

    # Mock plugin functions
    mock_plugins = {
        "ec2": mocker.Mock(return_value=ec2_mock_response),
        "s3": mocker.Mock(return_value=s3_mock_response),
        "rds": mocker.Mock(return_value=rds_mock_response),
    }

    # Mock ExtensionManager to return these plugins
    mock_extension_manager = mocker.Mock()
    mock_extension_manager.names.return_value = list(mock_plugins.keys())

    # Explicitly define __getitem__ to simulate dictionary-like behavior
    def get_plugin(name):
        print(f"Getting plugin: {name}")
        return mocker.Mock(plugin=mock_plugins[name])

    mock_extension_manager.__getitem__ = mocker.Mock(side_effect=get_plugin)

    # Patch assume_role with the correct module path
    mock_assume_role = mocker.patch(
        "cloudylist.main.assume_role",  # Correct module path
        autospec=True,
        side_effect=lambda account_id, role_name: {
            "AccessKeyId": "mock-key",
            "SecretAccessKey": "mock-secret",
            "SessionToken": "mock-token",
        },
    )
    print("Mock for assume_role is applied:", mock_assume_role)

    # Patch get_boto3_client
    mock_get_client = mocker.patch("cloudylist.utils.get_boto3_client", autospec=True)

    # Mock configuration
    mock_config = {
        "accounts": [{"account_id": "123456789012", "role_name": "TestRole"}],
        "regions": ["us-east-1", "us-west-2"],
    }

    # Call collect_inventory
    inventory = collect_inventory(mock_config, mock_extension_manager)

    # Debugging Outputs
    print("Inventory:", inventory)
    print("Assume Role Calls:", mock_assume_role.call_args_list)
    print("Get Client Calls:", mock_get_client.call_args_list)

    # Assertions
    assert len(inventory) == 6  # 3 plugins * 2 regions
    assert inventory[0]["service"] == "ec2"
    assert inventory[0]["resources"] == ec2_mock_response
    assert inventory[1]["service"] == "s3"
    assert inventory[1]["resources"] == s3_mock_response
    assert inventory[2]["service"] == "rds"
    assert inventory[2]["resources"] == rds_mock_response
    assert inventory[3]["region"] == "us-west-2"  # Ensure second region is covered

    # Confirm assume_role was called
    assert mock_assume_role.call_count == 1, "assume_role was not called as expected."


def test_output_table(mocker):
    """
    Test the output_table function.
    """
    # Mock data
    data = [
        {"account": "123456789012", "region": "us-east-1", "service": "ec2", "resources": [{"id": "i-123"}]},
    ]

    # Mock console output
    console = mocker.patch("rich.console.Console.print")
    output_table(data)

    # Assert that the console's print method was called
    console.assert_called_once()


def test_output_json(mocker):
    """
    Test the output_json function to ensure it prints the correct JSON output.
    """
    # Mock data
    data = [
        {"account": "123456789012", "region": "us-east-1", "service": "ec2", "resources": [{"id": "i-123"}]},
    ]

    # Patch the Console.print_json method
    mock_print_json = mocker.patch("cloudylist.main.Console.print_json", autospec=True)

    # Call output_json
    output_json(data)

    # Retrieve the actual call arguments
    args, kwargs = mock_print_json.call_args

    # Generate the expected JSON output
    expected_json = json.dumps(data, indent=4)

    # Assert that the correct data was passed to print_json
    assert kwargs["data"] == expected_json, f"Expected: {expected_json}, Got: {kwargs['data']}"


def test_output_yaml(mocker):
    """
    Test the output_yaml function to ensure it prints the correct YAML output.
    """
    # Mock data
    data = [
        {"account": "123456789012", "region": "us-east-1", "service": "ec2", "resources": [{"id": "i-123"}]},
    ]

    # Mock the Console.print method
    mock_console_print = mocker.patch("cloudylist.main.Console.print", autospec=True)

    # Call output_yaml
    output_yaml(data)

    # Assert that Console.print was called
    assert mock_console_print.called, "Console.print was not called."

    # Retrieve the actual arguments passed to Console.print
    args, kwargs = mock_console_print.call_args

    # Generate the expected YAML output
    expected_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)

    # Assert that the expected YAML is part of the arguments
    assert expected_yaml in args, f"Expected YAML was not printed: {expected_yaml}"
