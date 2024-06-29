# Install yum-config-manager to manage your repositories.
sudo yum install -y yum-utils
# Use yum-config-manager to add the official HashiCorp Linux repository.
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
# Install terraform
sudo yum -y install terraform

echo "Terraform Installed version:  $(terraform -v)"