def list_resources(client):
    """List EC2 instances."""
    instances = []
    response = client.describe_instances()
    for reservation in response.get("Reservations", []):
        for instance in reservation.get("Instances", []):
            instances.append(
                {
                    "InstanceId": instance["InstanceId"],
                    "State": instance["State"]["Name"],
                    "Type": instance["InstanceType"],
                }
            )
    return instances
