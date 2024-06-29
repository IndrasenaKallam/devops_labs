# Terraform

### Terrafom Setup for AWS 
1. Terraform installation
2. Make sure awscli is installed.
3. export AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

### Ec2 without modules

    ec2_without_modules/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── provider.tf
    └── ec2.tf

### Creating EC2 instances with modules

    ec2_with_modules/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    ├── provider.tf
    ├── modules/
    │   ├── vpc/
    │   │   ├── main.tf
    │   │   ├── variables.tf
    │   │   ├── outputs.tf
    │   ├── ec2/
    │   │   ├── main.tf
    │   │   ├── variables.tf
    │   │   ├── outputs.tf

