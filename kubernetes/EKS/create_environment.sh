:'
prereq:
1. create a bastion host and a bastion role with administrator access
2. create a bastion host security group with the following rules:
   - inbound: allow ssh from your ip
   - outbound: allow all
3. policies added to bastion instance:
    - AmazonSSMManagedInstanceCore
    - AdministratorAccess
'
#!/bin/bash

vpc_id=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications "ResourceType=vpc,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-eks-vpc}]" --query 'Vpc.VpcId' --output text)

echo "enabling hostname resolution on vpc ..."
aws ec2 modify-vpc-attribute --vpc-id $vpc_id --enable-dns-hostname

# Create subnets
subnet_1a=$(aws ec2 create-subnet \
  --vpc-id $vpc_id \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=owner,Value=kubedemy},{Key=Name,Value=ikallam-eks-subnet-1a}]" \
  --query 'Subnet.SubnetId' --output text)

subnet_1b=$(aws ec2 create-subnet \
  --vpc-id $vpc_id \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-eks-subnet-1b}]" \
  --query 'Subnet.SubnetId' --output text)

subnet_1c=$(aws ec2 create-subnet \
  --vpc-id $vpc_id \
  --cidr-block 10.0.3.0/24 \
  --availability-zone us-east-1c \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-eks-subnet-1c}]" \
  --query 'Subnet.SubnetId' --output text)


igw=$(aws ec2 create-internet-gateway --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-eks-ig}]" --query 'InternetGateway.InternetGatewayId' --output text)
echo "Internet Gateway ID: $igw"

# attach the internet gateway to the VPC
echo "Attaching Internet Gateway to VPC..."
aws ec2 attach-internet-gateway --vpc-id $vpc_id --internet-gateway-id $igw

aws ec2 modify-subnet-attribute --subnet-id $subnet_1a --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $subnet_1b --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $subnet_1c --map-public-ip-on-launch

$ Get the route table ID
route_table_id=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=$vpc_id" --query "RouteTables[0].RouteTableId" --output text)

# create a route in the route table to allow internet access
aws ec2 create-route \
  --route-table-id $route_table_id \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $igw


private_subnet_1a=$(aws ec2 create-subnet \
  --vpc-id $vpc_id \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=owner,Value=kubedemy},{Key=Name,Value=ikallam-eks-private-subnet-1a}]" \
  --query 'Subnet.SubnetId' --output text)

private_subnet_1b=$(aws ec2 create-subnet \
  --vpc-id $vpc_id \
  --cidr-block 10.0.12.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-eks-private-subnet-1b}]" \
  --query 'Subnet.SubnetId' --output text)

privat_subnet_1c=$(aws ec2 create-subnet \
  --vpc-id $vpc_id \
  --cidr-block 10.0.13.0/24 \
  --availability-zone us-east-1c \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-private-eks-subnet-1c}]" \
  --query 'Subnet.SubnetId' --output text)

private_route_table_id=$(aws ec2 create-route-table \
  --vpc-id $vpc_id \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-eks-private-route-table}]" --query 'RouteTable.RouteTableId' --output text)

aws ec2 associate-route-table \
  --route-table-id $private_route_table_id \
  --subnet-id $private_subnet_1a  

aws ec2 associate-route-table \
  --route-table-id $private_route_table_id \
  --subnet-id $private_subnet_1b

aws ec2 associate-route-table \
  --route-table-id $private_route_table_id \
  --subnet-id $private_subnet_1c


elastic_ip=$(aws ec2 allocate-address \
  --domain vpc \
  --tag-specifications "ResourceType=elastic-ip,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-eks-eip}]" \
  --query 'AllocationId' --output text)

# create a NAT gateway in the public subnet
natgateway=$(aws ec2 create-nat-gateway \
  --allocation-id $elastic_ip \
  --subnet-id $subnet_1a \
  --tag-specifications "ResourceType=natgateway,Tags=[{Key=owner,Value=ikallam},{Key=Name,Value=ikallam-natgateway}]" \
  --connectivity-type public \
  --query 'NatGateway.NatGatewayId' --output text)


aws ec2 create-route \
  --route-table-id $private_route_table_id \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $natgateway


sleep 5

echo "VPC ID: $vpc_id"
echo "Subnet 1a ID: $subnet_1a"
echo "Subnet 1b ID: $subnet_1b"
echo "Subnet 1c ID: $subnet_1c"
echo "Private Subnet 1a ID: $private_subnet_1a"
echo "Private Subnet 1b ID: $private_subnet_1b"
echo "Private Subnet 1c ID: $privat_subnet_1c"
echo "route table ID: $route_table_id"
echo "internet gateway ID: $igw"
echo "Elastic IP: $elastic_ip"
echo "NAT Gateway ID: $natgateway"
echo "Private Route Table ID: $private_route_table_id"
