resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"

  ingress {
    description      = "SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"] # Replace with your IP or CIDR range for production
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "main_app_deploy" {
  ami           = var.ami_os
  instance_type = "t2.micro"
  tags = {
    Name = var.instance_name
  }
  vpc_security_group_ids = [aws_security_group.allow_ssh.id]

  root_block_device {
    volume_type           = "gp3"  # Change to the desired volume type, e.g., gp2
    volume_size           = var.volume_size     # Specify the size in GB
    delete_on_termination = true   # Set to false if you want to keep the volume after instance termination
  }


}

resource "aws_security_group" "my-custom-security-group" {
  name        = "my-custom-security-group"
  description = "Security group for my application"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # This is very permissive; restrict as needed
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # This is very permissive; restrict as needed
  }
}

resource "aws_security_group_rule" "custom_tcp_ingress" {
  type                     = "ingress"
  from_port                = var.post_number
  to_port                  = var.post_number
  protocol                 = "tcp"
  cidr_blocks              = ["0.0.0.0/0"]
  security_group_id        = aws_security_group.my-custom-security-group.id
}

resource "aws_security_group_rule" "custom_22_tcp_ingress" {
  type                     = "ingress"
  from_port                = 22
  to_port                  = 22
  protocol                 = "tcp"
  cidr_blocks              = ["0.0.0.0/0"]
  security_group_id        = aws_security_group.my-custom-security-group.id
}

resource "aws_security_group_rule" "custom_80_tcp_ingress" {
  type                     = "ingress"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  cidr_blocks              = ["0.0.0.0/0"]
  security_group_id        = aws_security_group.my-custom-security-group.id
}

resource "aws_security_group_rule" "custom_443_tcp_ingress" {
  type                     = "ingress"
  from_port                = 443
  to_port                  = 443
  protocol                 = "tcp"
  cidr_blocks              = ["0.0.0.0/0"]
  security_group_id        = aws_security_group.my-custom-security-group.id
}

// ... rest of your configuration ...
// ... existing code ...


resource "aws_ecr_repository" "main_app_deploy" {
  name = var.aws_ecr_repository_name
  tags = {
    Name = "latest"
  }
}



output "ec2_public_ipv4" {
  description = "EC2 Public IP"
  value = aws_instance.main_app_deploy.public_ip
}

output "ecr_repository_uri" {
  description = "URI of ECR Repository"
  value = aws_ecr_repository.main_app_deploy.repository_url
}