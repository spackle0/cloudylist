def list_resources(client):
    """List S3 buckets."""
    response = client.list_buckets()
    return [
        {"Name": bucket["Name"], "CreationDate": str(bucket["CreationDate"])} for bucket in response.get("Buckets", [])
    ]
