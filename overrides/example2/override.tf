resource "aws_instance" "example" {
  ami = "ami-0b72821e2f351e396"

    ebs_block_device {
      device_name = "/dev/sda1"
      volume_size = 16
    }

    tags = {
      Name = "example-instance-override"
    }
}
