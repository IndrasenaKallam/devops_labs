locals {
    combined_list               = concat(module.vpc.private_subnets, module.vpc.public_subnets)
}
data "aws_ssm_parameter" "ami_id" {
  name = "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"
}

# creating a vpc using module
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "test-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Name        = "test-vpc"
    Environment = "dev"
  }
}

# create security groups using resource block
resource "aws_security_group" "my_sg" {
  name        = join("_", ["sg", "module.vpc.vpc_id"])
  description = "security group for vpc"
  vpc_id      = module.vpc.vpc_id
  dynamic "ingress" {
    for_each = var.rules
    content {
      from_port   = ingress.value["port"]
      protocol    = ingress.value["proto"]
      to_port     = ingress.value["port"]
      cidr_blocks = ingress.value["cidr_blocks"]
    }
  }
  tags = {
    Name = "allow_tls"
  }
}


resource "aws_instance" "my-instance" {
  
  count                       = length(local.combined_list)
  ami                         = data.aws_ssm_parameter.ami_id.value
  subnet_id                   = local.combined_list[count.index]
  instance_type               = "t3.micro"
  security_groups             = [aws_security_group.my_sg.id]
  associate_public_ip_address = true
  user_data                   = fileexists("script.sh") ? file("script.sh") : null

}
