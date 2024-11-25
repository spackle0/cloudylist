import typer
import json
import yaml
from rich.console import Console
from rich.table import Table
from cloudylist.utils import collect_inventory, load_config
from stevedore import ExtensionManager

app = typer.Typer()
console = Console()

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
