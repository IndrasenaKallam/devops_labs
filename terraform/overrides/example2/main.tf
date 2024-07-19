provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "example" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
  
  lifecycle {
    create_before_destroy = false
    ignore_changes        = [ami]
  }
  
  ebs_block_device {
    device_name = "/dev/sda1"
    volume_size = 8
  }
  
  ebs_block_device {
    device_name = "/dev/sdb"
    volume_size = 50
  }
  tags = {
    Name = "example-instance"
    Env  = "development"
  }
}
