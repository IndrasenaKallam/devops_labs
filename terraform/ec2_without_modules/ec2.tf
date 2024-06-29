# ec2.tf

resource "aws_instance" "main" {
  ami           = var.instance_ami
  instance_type = var.instance_type
  key_name      = var.key_name


  network_interface {
    device_index              = 0
    network_interface_id = aws_network_interface.test.id
  }

  tags = {
    Name = "AdvancedEC2Instance"
  }
}
