import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


def get_vpc_by_name(ec2, vpc_name):
    """Check if a VPC with the given name already exists."""
    try:
        response = ec2.describe_vpcs(
            Filters=[
                {'Name': 'tag:Name', 'Values': [vpc_name]}
            ]
        )
        vpcs = response.get('Vpcs', [])
        if vpcs:
            return vpcs[0]['VpcId']  # Return the first matching VPC ID
        return None
    except Exception as e:
        print(f"[❌] Error while checking for existing VPC: {str(e)}")
        return None
def create_vpc(cidr_block, owner, vpc_name, region='us-east-1'):
    try:
        # Initialize the EC2 client with a specific region
        # Check if a VPC with the same name already exists
        existing_vpc_id = get_vpc_by_name(ec2, vpc_name)
        if existing_vpc_id:
            print(f"[⚠️] VPC with name '{vpc_name}' already exists. VPC ID: {existing_vpc_id}")
            return existing_vpc_id

        # Create the VPC
        response = ec2.create_vpc(
            CidrBlock=cidr_block,
            TagSpecifications=[
                {
                    'ResourceType': 'vpc',
                    'Tags': [
                        {'Key': 'owner', 'Value': owner},
                        {'Key': 'Name', 'Value': vpc_name}
                    ]
                }
            ]
        )

        # Extract the VPC ID
        vpc_id = response['Vpc']['VpcId']
        print(f"[✅] Successfully created VPC with ID: {vpc_id}")
        return vpc_id

    except NoCredentialsError:
        print("[❌] Error: No AWS credentials found. Please configure your credentials.")
    except PartialCredentialsError:
        print("[❌] Error: Incomplete AWS credentials configuration.")
    except Exception as e:
        print(f"[❌] Error: {str(e)}")

def get_subnet_by_name(ec2, subnet_name):
    """Check if a subnet with the given name already exists."""
    try:
        response = ec2.describe_subnets(
            Filters=[
                {'Name': 'tag:Name', 'Values': [subnet_name]}
            ]
        )
        subnets = response.get('Subnets', [])
        if subnets:
            return subnets[0]['SubnetId']  # Return the first matching Subnet ID
        return None
    except Exception as e:
        print(f"[❌] Error while checking for existing subnet: {str(e)}")
        return None


def create_subnet(vpc_id, cidr_block, subnet_name, availability_zone, is_public, region='us-east-1'):
    try:
        # Initialize the EC2 client with a specific region
        ec2 = boto3.client('ec2', region_name=region)

        # Check if a subnet with the same name already exists
        existing_subnet_id = get_subnet_by_name(ec2, subnet_name)
        if existing_subnet_id:
            print(f"[⚠️] Subnet with name '{subnet_name}' already exists. Subnet ID: {existing_subnet_id}")
            return existing_subnet_id

        # Create the subnet
        response = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=cidr_block,
            AvailabilityZone=availability_zone,
            TagSpecifications=[
                {
                    'ResourceType': 'subnet',
                    'Tags': [
                        {'Key': 'Name', 'Value': subnet_name},
                        {'Key': 'Type', 'Value': 'Public' if is_public else 'Private'}
                    ]
                }
            ]
        )

        # Extract the Subnet ID
        subnet_id = response['Subnet']['SubnetId']
        print(f"[✅] Successfully created {'Public' if is_public else 'Private'} Subnet with ID: {subnet_id}")
        if is_public:
            ec2.modify_subnet_attribute(
                SubnetId=subnet_id,
                MapPublicIpOnLaunch={'Value': True}
            )
            print(f"[✅] Auto-assign public IP enabled for Subnet ID: {subnet_id}")
        return subnet_id

    except NoCredentialsError:
        print("[❌] Error: No AWS credentials found. Please configure your credentials.")
    except PartialCredentialsError:
        print("[❌] Error: Incomplete AWS credentials configuration.")
    except Exception as e:
        print(f"[❌] Error: {str(e)}")

def create_subnets(vpc_id, subnets, is_public, region='us-east-1'):
    """Create multiple subnets based on the provided dictionary."""
    for az, cidr_block in subnets.items():
        subnet_name = f"{'public' if is_public else 'private'}_subnet_{az}"
        create_subnet(vpc_id, cidr_block, subnet_name, az, is_public, region)


def get_default_route_table(vpc_id, region='us-east-1'):
    """Retrieve the default route table for a given VPC."""
    try:
        # Initialize the EC2 client with a specific region
        ec2 = boto3.client('ec2', region_name=region)

        # Describe route tables filtered by the VPC ID
        response = ec2.describe_route_tables(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]}
            ]
        )

        # Iterate through the route tables to find the default one
        for route_table in response.get('RouteTables', []):
            for association in route_table.get('Associations', []):
                if association.get('Main'):  # Check if it's the main route table
                    print(f"[✅] Default Route Table ID: {route_table['RouteTableId']}")
                    return route_table['RouteTableId']

        print("[⚠️] No default route table found for the given VPC.")
        return None

    except NoCredentialsError:
        print("[❌] Error: No AWS credentials found. Please configure your credentials.")
    except PartialCredentialsError:
        print("[❌] Error: Incomplete AWS credentials configuration.")
    except Exception as e:
        print(f"[❌] Error: {str(e)}")

def get_existing_internet_gateway(vpc_id, region):
    """
    Check if an Internet Gateway already exists for the given VPC.

    :param vpc_id: The ID of the VPC.
    :param region: The AWS region.
    :return: The ID of the existing Internet Gateway, or None if not found.
    """
    ec2 = boto3.client('ec2', region_name=region)
    try:
        response = ec2.describe_internet_gateways(
            Filters=[
                {'Name': 'attachment.vpc-id', 'Values': [vpc_id]}
            ]
        )
        igws = response.get('InternetGateways', [])
        if igws:
            igw_id = igws[0]['InternetGatewayId']
            print(f"[⚠️] Internet Gateway already exists with ID: {igw_id}")
            return igw_id
        else:
            print("[ℹ️] No existing Internet Gateway found for this VPC.")
            return None
    except Exception as e:
        print(f"[❌] Error checking Internet Gateway: {str(e)}")
        return None
def create_and_attach_internet_gateway(vpc_id, region='us-east-1'):
    """
    Create an Internet Gateway and attach it to the specified VPC.

    :param vpc_id: The ID of the VPC to attach the Internet Gateway to.
    :param region: The AWS region where the VPC exists.
    :return: The ID of the created Internet Gateway.
    """
    try:
        # Initialize the EC2 client
        ec2 = boto3.client('ec2', region_name=region)

        # Create the Internet Gateway
        igw_response = ec2.create_internet_gateway()

        internet_gateway_id = igw_response['InternetGateway']['InternetGatewayId']

        # Apply tags to the Internet Gateway
        ec2.create_tags(
            Resources=[internet_gateway_id],
            Tags=[
                {'Key': 'owner', 'Value': owner},
                {'Key': 'Name', 'Value': vpc_name}
            ]
        )
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        print(f"[✅] Internet Gateway created with ID: {igw_id}")

        # Attach the Internet Gateway to the VPC
        ec2.attach_internet_gateway(
            InternetGatewayId=igw_id,
            VpcId=vpc_id
        )
        print(f"[✅] Internet Gateway {igw_id} attached to VPC {vpc_id}")

        return igw_id

    except Exception as e:
        print(f"[❌] Error: {str(e)}")
        return None

def get_or_create_route_table(vpc_id, route_table_name, owner, region='us-east-1'):
    """
    Check if a route table with the specified name exists in the VPC.
    If it doesn't exist, create and tag the route table.

    :param vpc_id: The ID of the VPC.
    :param route_table_name: The name of the route table to check or create.
    :param owner: The owner tag value.
    :param region: The AWS region where the VPC exists.
    :return: The ID of the existing or newly created route table.
    """
    try:
        # Initialize the EC2 client
        ec2 = boto3.client('ec2', region_name=region)

        # Describe route tables in the VPC
        response = ec2.describe_route_tables(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Name', 'Values': [route_table_name]}
            ]
        )

        # Check if a route table with the specified name exists
        if response['RouteTables']:
            route_table_id = response['RouteTables'][0]['RouteTableId']
            print(f"[✅] Route Table with name '{route_table_name}' already exists: {route_table_id}")
            return route_table_id

        # Create a new route table if it doesn't exist
        route_table_response = ec2.create_route_table(VpcId=vpc_id)
        route_table_id = route_table_response['RouteTable']['RouteTableId']
        print(f"[✅] Created new Route Table with ID: {route_table_id}")

        # Tag the new route table
        ec2.create_tags(
            Resources=[route_table_id],
            Tags=[
                {'Key': 'owner', 'Value': owner},
                {'Key': 'Name', 'Value': route_table_name}
            ]
        )
        print(f"[✅] Tagged Route Table {route_table_id} with Name: {route_table_name}")

        return route_table_id

    except Exception as e:
        print(f"[❌] Error: {str(e)}")
        return None

def associate_private_subnets_to_route_table(vpc_id, route_table_name, region='us-east-1'):
    """
    Associate all subnets with names containing 'private_subnet' in the VPC to the specified route table.

    :param vpc_id: The ID of the VPC.
    :param route_table_name: The name of the route table to associate with private subnets.
    :param region: The AWS region where the VPC exists.
    """
    try:
        # Initialize the EC2 client
        ec2 = boto3.client('ec2', region_name=region)

        # Get the route table ID by name
        route_table_response = ec2.describe_route_tables(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Name', 'Values': [route_table_name]}
            ]
        )
        if not route_table_response['RouteTables']:
            print(f"[❌] Route table with name '{route_table_name}' not found.")
            return

        route_table_id = route_table_response['RouteTables'][0]['RouteTableId']
        print(f"[✅] Found Route Table '{route_table_name}' with ID: {route_table_id}")

        # Get all subnets with names containing 'private_subnet'
        subnets_response = ec2.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Name', 'Values': ['*private_subnet*']}
            ]
        )

        # Extract subnet IDs
        private_subnets = [subnet['SubnetId'] for subnet in subnets_response['Subnets']]
        if not private_subnets:
            print(f"[❌] No subnets with names containing 'private_subnet' found in VPC {vpc_id}.")
            return

        # Associate private subnets with the route table
        for subnet_id in private_subnets:
            # Check if the subnet is already associated with the route table
            route_table_associations = ec2.describe_route_tables(
                Filters=[
                    {'Name': 'association.subnet-id', 'Values': [subnet_id]}
                ]
            )
            
            already_associated = False
            for route_table in route_table_associations['RouteTables']:
                for association in route_table.get('Associations', []):
                    if association.get('RouteTableId') == route_table_id:
                        already_associated = True
                        break
                if already_associated:
                    break

            if not already_associated:
                # Associate the subnet if not already associated
                ec2.associate_route_table(
                    RouteTableId=route_table_id,
                    SubnetId=subnet_id
                )
                print(f"[✅] Associated Subnet {subnet_id} with Route Table {route_table_id}")
            else:
                print(f"[ℹ️] Subnet {subnet_id} is already associated with Route Table {route_table_id}")

    except Exception as e:
        print(f"[❌] An error occurred: {e}")


def create_nat_gateway_and_update_routes(vpc_id, private_rtb_name, public_subnet_id, region='us-east-1'):
    """
    Create a NAT Gateway and update the routes in the private route table.
    If a NAT Gateway already exists in the VPC, reuse it.

    :param vpc_id: The ID of the VPC.
    :param private_rtb_name: The name of the private route table.
    :param public_subnet_id: The ID of the public subnet where the NAT Gateway will be created.
    :param region: The AWS region.
    """
    try:
        ec2 = boto3.client('ec2', region_name=region)

        # Step 1: Check if a NAT Gateway already exists in the VPC
        print("[ℹ️] Checking for existing NAT Gateways in the VPC...")
        nat_gateways_response = ec2.describe_nat_gateways(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'state', 'Values': ['available', 'pending']}
            ]
        )
        existing_nat_gateways = nat_gateways_response.get('NatGateways', [])

        if existing_nat_gateways:
            nat_gateway_id = existing_nat_gateways[0]['NatGatewayId']
            print(f"[✅] Found existing NAT Gateway with ID: {nat_gateway_id}")
        else:
            # Step 2: Allocate an Elastic IP for the NAT Gateway
            eip_response = ec2.allocate_address(Domain='vpc')
            allocation_id = eip_response['AllocationId']
            print(f"[✅] Allocated Elastic IP with Allocation ID: {allocation_id}")

            # Step 3: Create the NAT Gateway in the public subnet
            nat_gateway_response = ec2.create_nat_gateway(
                SubnetId=public_subnet_id,
                AllocationId=allocation_id
            )
            nat_gateway_id = nat_gateway_response['NatGateway']['NatGatewayId']
            print(f"[✅] Created NAT Gateway with ID: {nat_gateway_id}")

            # Wait for the NAT Gateway to become available
            waiter = ec2.get_waiter('nat_gateway_available')
            print("[ℹ️] Waiting for the NAT Gateway to become available...")
            waiter.wait(NatGatewayIds=[nat_gateway_id])
            print(f"[✅] NAT Gateway {nat_gateway_id} is now available.")

        # Step 4: Get the Route Table ID for the private route table
        route_table_response = ec2.describe_route_tables(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'tag:Name', 'Values': [private_rtb_name]}
            ]
        )
        if not route_table_response['RouteTables']:
            print(f"[❌] Route table with name '{private_rtb_name}' not found.")
            return

        private_rtb_id = route_table_response['RouteTables'][0]['RouteTableId']
        print(f"[✅] Found Private Route Table '{private_rtb_name}' with ID: {private_rtb_id}")

        # Step 5: Update the private route table to route traffic through the NAT Gateway
        ec2.create_route(
            RouteTableId=private_rtb_id,
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=nat_gateway_id
        )
        print(f"[✅] Updated Route Table {private_rtb_id} to route traffic through NAT Gateway {nat_gateway_id}")

    except Exception as e:
        print(f"[❌] An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    owner       = "ikallam"
    cidr_block  = "10.0.0.0/16"
    vpc_name    = f"{owner}-testing-vpc"
    region_name = "us-east-1"
    ec2 = boto3.client('ec2', region_name=region_name)
    vpc_id = create_vpc(cidr_block, owner, vpc_name, region_name)
    # Public Subnets
    public_subnets = {
        "us-east-1a": "10.0.1.0/24",
        "us-east-1b": "10.0.2.0/24",
        "us-east-1c": "10.0.3.0/24"
    }
    create_subnets(vpc_id, public_subnets, is_public=True, region=region_name)

    # Private Subnets
    private_subnets = {
        "us-east-1a": "10.0.11.0/24",
        "us-east-1b": "10.0.12.0/24",
        "us-east-1c": "10.0.13.0/24"
    }
    create_subnets(vpc_id, private_subnets, is_public=False, region=region_name)

    # create internet gateway for public subnets
    internet_gateway_id = get_existing_internet_gateway(vpc_id, region_name)
    if not internet_gateway_id:
        # Create Internet Gateway if it doesn't exist
        internet_gateway_id = create_and_attach_internet_gateway(vpc_id, region='us-east-1')

    default_route_table_id = get_default_route_table(vpc_id, region=region_name)
    ec2.create_tags(
            Resources=[default_route_table_id],
            Tags=[
                {'Key': 'owner', 'Value': owner},
                {'Key': 'Name', 'Value': "public_rtb"}
            ]
        )
    # create private route table
    private_route_table_id = get_or_create_route_table(vpc_id=vpc_id,route_table_name="private_rtb",owner=owner,region=region_name)
    # associate private subnet to private route table
    associate_private_subnets_to_route_table( vpc_id=vpc_id,route_table_name="private_rtb",region="us-east-1")

    ec2.create_route(RouteTableId=default_route_table_id,DestinationCidrBlock="0.0.0.0/0",GatewayId=internet_gateway_id)
    print(f"[✅] Internet Gateway {internet_gateway_id} attached to Public Route Table {default_route_table_id}")
    create_nat_gateway_and_update_routes(vpc_id=vpc_id, private_rtb_name="private_rtb", public_subnet_id=get_subnet_by_name(ec2, "public_subnet_us-east-1a"), region=region_name)