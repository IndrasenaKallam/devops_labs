provider "aws" {
  region = data.aws_region.current.name

  assume_role {
    role_arn = "arn:aws:iam::${account_number}:role/ikallam-bastion-role"
  }
}