data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "aws_caller_identity" "current" {}

locals {
}



resource "aws_iam_role" "tantar_ec2" {
  name = "tantar-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_instance_profile" "tantar" {
  name = "tantar-ec2-profile"
  role = aws_iam_role.tantar_ec2.name
}



resource "aws_security_group" "tantar" {
  name        = "tantar-sg"
  description = "Tantar inbound HTTP/HTTPS and SSH"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.admin_cidr]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "tantar-sg"
  }
}

resource "aws_instance" "tantar" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnets.default.ids[0]
  vpc_security_group_ids      = [aws_security_group.tantar.id]
  key_name                    = var.ssh_key_name
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.tantar.name

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    app_repo_url        = var.app_repo_url
    app_repo_ref        = var.app_repo_ref
    compose_project_dir = var.compose_project_dir
    compose_file        = var.compose_file
    acme_email          = var.acme_email
    front_host          = var.front_host
    api_host            = var.api_host
    app_env_extra       = var.app_env_extra
    aws_region          = var.aws_region
  })

  tags = {
    Name = "tantar"
  }
}
