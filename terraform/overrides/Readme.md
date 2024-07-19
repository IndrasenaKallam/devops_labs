# Example 1

main.tf
```
resource "aws_instance" "web" {
  instance_type = "t2.micro"
  ami           = "ami-408c7f28"
}
```
override.tf
```
resource "aws_instance" "web" {
  ami = "foo"
}
```

finalmain.tf
```
resource "aws_instance" "web" {
  instance_type = "t2.micro"
  ami           = "foo"
}
```

# Example 2

main.tf
```
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


# override.tf 
resource "aws_instance" "example" {
  ami = "ami-0b72821e2f351e396"

  override {
    lifecycle {
      create_before_destroy = true
    }

    ebs_block_device {
      device_name = "/dev/sda1"
      volume_size = 16
    }

    tags = {
      Name = "example-instance-override"
    }
  }
}


```
final.tf
```
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "example" {
  ami           = "ami-0b72821e2f351e396"  # From override.tf
  
  instance_type = "t2.micro"
  
  lifecycle {
    create_before_destroy = true  # From override.tf
    ignore_changes        = [ami]  # Retained from main.tf
  }
  
  ebs_block_device {
    device_name = "/dev/sda1"
    volume_size = 16  # From override.tf
  }

  # The ebs_block_device block with device_name = "/dev/sdb" is removed since it's not in override.tf.
  
  tags = {
    Name = "example-instance-override"  # From override.tf
  }
}

```


