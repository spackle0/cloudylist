def list_resources(client):
    """List RDS instances."""
    response = client.describe_db_instances()
    return [
        {"DBInstanceIdentifier": db["DBInstanceIdentifier"], "Status": db["DBInstanceStatus"]}
        for db in response.get("DBInstances", [])
    ]
