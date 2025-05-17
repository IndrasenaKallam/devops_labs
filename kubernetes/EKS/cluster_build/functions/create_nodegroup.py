import boto3

def create_eks_nodegroup(cluster_name, nodegroup_name, scaling_config, subnets, node_role, instance_types, ami_type, capacity_type, update_config, taints, labels, tags):
    """
    Create an EKS node group with the specified configuration.

    :param cluster_name: Name of the EKS cluster.
    :param nodegroup_name: Name of the node group.
    :param scaling_config: Dictionary with minSize, maxSize, and desiredSize.
    :param subnets: List of subnet IDs.
    :param node_role: ARN of the IAM role for the node group.
    :param ssh_key: Name of the EC2 SSH key pair.
    :param instance_types: List of instance types.
    :param ami_type: AMI type for the node group.
    :param capacity_type: Capacity type (e.g., ON_DEMAND or SPOT).
    :param update_config: Dictionary with maxUnavailable.
    :param taints: List of taints (key, value, effect).
    :param labels: Dictionary of labels.
    :param tags: Dictionary of tags.
    """
    eks_client = boto3.client('eks',region_name='us-east-1')

    try:
        response = eks_client.create_nodegroup(
            clusterName=cluster_name,
            nodegroupName=nodegroup_name,
            scalingConfig=scaling_config,
            subnets=subnets,
            nodeRole=node_role,
            instanceTypes=instance_types,
            amiType=ami_type,
            capacityType=capacity_type,
            updateConfig=update_config,
            taints=taints,
            labels=labels,
            tags=tags
        )
        print(f"Node group '{nodegroup_name}' creation initiated successfully.")
        print(f"Waiting for node group '{nodegroup_name}' to become active...")
        waiter = eks_client.get_waiter('nodegroup_active')
        waiter.wait(
            clusterName=cluster_name,
            nodegroupName=nodegroup_name,
            WaiterConfig={
                'Delay': 30,  # Wait 30 seconds between checks
                'MaxAttempts': 40  # Maximum number of attempts (40 * 30 = 20 minutes)
            }
        )
        print(f"Node group '{nodegroup_name}' is now active.")
        return response
    except Exception as e:
        print(f"Error creating node group: {e}")
        return None