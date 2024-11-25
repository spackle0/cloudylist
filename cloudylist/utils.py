import logging
import boto3
import yaml
from botocore.exceptions import ClientError
from typing import List, Dict, Any

# Configure logging
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger(__name__)


def load_config(config_file: str = "config.yml") -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def assume_role(account_id: str, role_name: str) -> Dict[str, str]:
    """Assume an IAM role in a target AWS account."""
    sts_client = boto3.client("sts")
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    try:
        response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="MultiAccountInventorySession")
        return response["Credentials"]
    except ClientError as e:
        logger.error(f"Failed to assume role {role_arn}: {e}")
        raise


def get_boto3_client(service: str, credentials: Dict[str, str], region: str) -> boto3.client:
    """Return a Boto3 client for a specific service."""
    return boto3.client(
        service,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region,
    )


def collect_inventory(config: Dict[str, Any], plugins: Any) -> List[Dict[str, Any]]:
    """Collect inventory across accounts and regions using plugins."""
    inventory = []
    for account in config["accounts"]:
        try:
            logger.info(f"Assuming role for account: {account['account_id']}")
            credentials = assume_role(account["account_id"], account["role_name"])
        except Exception as e:
            logger.error(f"Error assuming role for account {account['account_id']}: {e}")
            continue

        for region in config["regions"]:
            for plugin_name in plugins.names():
                try:
                    logger.info(f"Querying plugin: {plugin_name} in region: {region}")
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
                    logger.error(f"Error querying {plugin_name} in {region} for account {account['account_id']}: {e}")
    return inventory
