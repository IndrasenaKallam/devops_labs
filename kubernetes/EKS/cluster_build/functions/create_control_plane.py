import boto3

def create_eks_cluster(cluster_name, role_arn, subnet_ids, public_access_cidrs, service_ipv4_cidr, kubernetes_version, tags):
    """
    Create an EKS cluster with the specified configuration.

    :param cluster_name: Name of the EKS cluster.
    :param role_arn: ARN of the IAM role for the EKS cluster.
    :param subnet_ids: List of subnet IDs for the cluster.
    :param public_access_cidrs: List of CIDR blocks for public access.
    :param service_ipv4_cidr: CIDR block for Kubernetes service IPs.
    :param kubernetes_version: Kubernetes version for the cluster.
    :param tags: Dictionary of tags to apply to the cluster.
    """
    
    try:
        eks_client = boto3.client('eks',region_name='us-east-1')
        response = eks_client.create_cluster(
            name=cluster_name,
            roleArn=role_arn,
            resourcesVpcConfig={
                'subnetIds': subnet_ids,
                'endpointPublicAccess': True,
                'publicAccessCidrs': public_access_cidrs
            },
            kubernetesNetworkConfig={
                'serviceIpv4Cidr': service_ipv4_cidr,
                'ipFamily': 'ipv4'
            },
            version=kubernetes_version,
            tags=tags
        )
        print(f"EKS cluster '{cluster_name}' creation initiated successfully.")
        print(f"Waiting for cluster '{cluster_name}' to become active...")
        waiter = eks_client.get_waiter('cluster_active')
        waiter.wait(
            name=cluster_name,
            WaiterConfig={
                'Delay': 30,  # Wait 30 seconds between checks
                'MaxAttempts': 40  # Maximum number of attempts (40 * 30 = 20 minutes)
            }
        )
        print(f"Node group '{cluster_name}' is now active.")
        return response
    except Exception as e:
        print(f"Error creating EKS cluster: {e}")
        return None