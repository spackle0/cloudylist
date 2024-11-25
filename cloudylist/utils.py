import boto3
import yaml


def load_config(config_file="config.yml"):
    """Load configuration from a YAML file."""
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def assume_role(account_id, role_name):
    """Assume an IAM role in a target AWS account."""
    sts_client = boto3.client("sts")
    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
    response = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="MultiAccountInventorySession")
    return response["Credentials"]


def get_boto3_client(service, credentials, region):
    """Return a Boto3 client for a specific service."""
    return boto3.client(
        service,
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region,
    )
