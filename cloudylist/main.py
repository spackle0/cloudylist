import typer
import json
import yaml
from rich.console import Console
from rich.table import Table
from cloudylist.utils import load_config, assume_role, get_boto3_client
from stevedore import ExtensionManager

app = typer.Typer()
console = Console()


# Collect inventory across accounts and regions
def collect_inventory(config, plugins):
    inventory = []
    for account in config["accounts"]:
        try:
            print(f"Assuming role for account: {account['account_id']}")
            credentials = assume_role(account["account_id"], account["role_name"])
        except Exception as e:
            print(f"Error assuming role for account {account['account_id']}: {e}")
            continue

        for region in config["regions"]:
            for plugin_name in plugins.names():
                try:
                    print(f"Querying plugin: {plugin_name} in region: {region}")
                    plugin = plugins[plugin_name].plugin
                    client = get_boto3_client(plugin_name, credentials, region)
                    resources = plugin(client)
                    inventory.append({
                        "account": account["account_id"],
                        "region": region,
                        "service": plugin_name,
                        "resources": resources,
                    })
                except Exception as e:
                    print(f"Error querying {plugin_name} in {region} for account {account['account_id']}: {e}")
    return inventory



def output_table(data):
    table = Table(title="AWS Multi-Account Inventory")
    table.add_column("Account", style="cyan", justify="left")
    table.add_column("Region", style="green", justify="left")
    table.add_column("Service", style="magenta", justify="left")
    table.add_column("Resources", justify="left")
    for item in data:
        resources_summary = f"{len(item['resources'])} resources"
        table.add_row(item["account"], item["region"], item["service"], resources_summary)
    console.print(table)


def output_json(data):
    console.print_json(data=json.dumps(data, indent=4))


def output_yaml(data):
    yaml_output = yaml.dump(data, default_flow_style=False, sort_keys=False)
    console.print(yaml_output)


@app.command()
def show_inventory(
    config_file: str = typer.Option("config.yml", help="Path to the configuration file."),
    format: str = typer.Option("table", help="Output format: table, json, yaml"),
):
    config = load_config(config_file)
    plugins = ExtensionManager(namespace="resources", invoke_on_load=False, verify_requirements=False)

    inventory = collect_inventory(config, plugins)

    if format == "table":
        output_table(inventory)
    elif format == "json":
        output_json(inventory)
    elif format == "yaml":
        output_yaml(inventory)
    else:
        console.print(f"[red]Invalid format:[/red] {format}", style="bold red")


if __name__ == "__main__":
    app()
