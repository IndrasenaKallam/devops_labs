import boto3
from create_vpc_private_public_subnets import get_subnet_by_name
from functions.helper import get_account_number
from functions.create_control_plane import create_eks_cluster
from functions.create_role_with_policies import create_iam_role
from create_vpc_private_public_subnets import get_subnet_by_name
from functions.create_nodegroup import create_eks_nodegroup

control_plane_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "Service": "eks.amazonaws.com"
                }
            }
        ]
    }

worker_nodes_trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            }
        }
    ]
}


control_plane_role_name = "ikallam-cluster-role"
control_plane_policies = ["arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"]
control_plane_tags = [{"Key": "owner", "Value": "ikallam"}]

worker_nodes_role_name = "ikallam-worker-role"
worker_nodes_policies = ["arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy","arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly","arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"]
worker_node_role_tags = [{"Key": "owner", "Value": "ikallam"}]

# clients
eks_client = boto3.client('eks',region_name='us-east-1')
ec2 = boto3.client('ec2',region_name='us-east-1')

# EKS cluster configuration
cluster_name = "ikallam-public-cluster"
role_arn = f"arn:aws:iam::{get_account_number()}:role/ikallam-cluster-role"
node_role = f"arn:aws:iam::{get_account_number()}:role/ikallam-worker-role"

subnet_ids = [
    get_subnet_by_name(ec2, "public_subnet_us-east-1a"),
    get_subnet_by_name(ec2, "public_subnet_us-east-1b"),
    get_subnet_by_name(ec2, "public_subnet_us-east-1c")
]
public_access_cidrs = ["0.0.0.0/0"]
service_ipv4_cidr = "172.20.0.0/16"
kubernetes_version = "1.28"
tags = {"owner": "ikallam", "environment": "development", "Name": f"{cluster_name}"}

    
system_nodegroup_name = "system-managed-workers-001"
application_nodegroup_name = "application-managed-workers-001"
scaling_config = { "minSize": 2, "maxSize": 5, "desiredSize": 2}
instance_types = ["t3.medium"]
ami_type = "AL2_x86_64"
capacity_type = "ON_DEMAND"
update_config = {"maxUnavailable": 1}

system_taints = [
    {"key": "CriticalAddonsOnly", "value": "true", "effect": "NO_SCHEDULE"},
    {"key": "CriticalAddonsOnly", "value": "true", "effect": "NO_EXECUTE"}
]

application_taints = []
system_labels = {
    "node.kubernetes.io/scope": "system"
}
application_labels = {
    "node.kubernetes.io/scope": "application"
}

# create roles and attach policies
create_iam_role(control_plane_role_name, control_plane_trust_policy, control_plane_policies, control_plane_tags)
create_iam_role(worker_nodes_role_name, worker_nodes_trust_policy, worker_nodes_policies, worker_node_role_tags)
create_eks_cluster(cluster_name, role_arn, subnet_ids, public_access_cidrs, service_ipv4_cidr, kubernetes_version, tags)
create_eks_nodegroup(cluster_name, system_nodegroup_name, scaling_config, subnet_ids, node_role, instance_types, ami_type, capacity_type, update_config, system_taints, system_labels, tags)
create_eks_nodegroup(cluster_name, application_nodegroup_name, scaling_config, subnet_ids, node_role, instance_types, ami_type, capacity_type, update_config, application_taints, application_labels, tags)