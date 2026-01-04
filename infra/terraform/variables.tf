variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "instance_type" {
  type    = string
  default = "t3.medium"
}

variable "ssh_key_name" {
  type = string
}

variable "admin_cidr" {
  type    = string
  default = "0.0.0.0/0"
}

variable "app_repo_url" {
  type = string
}

variable "app_repo_ref" {
  type    = string
  default = "main"
}

variable "acme_email" {
  type = string
}

variable "front_host" {
  type = string
}

variable "api_host" {
  type = string
}

variable "compose_project_dir" {
  type    = string
  default = "/opt/tantar"
}

variable "compose_file" {
  type    = string
  default = "docker-compose.yml"
}

variable "app_env_extra" {
  type    = string
  default = ""
}


