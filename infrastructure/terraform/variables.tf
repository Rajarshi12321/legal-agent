variable "region"{
    default = "ap-south-1"
}

variable "ami_os"{
    default = "ami-0f58b397bc5c1f2e8"  # Ubuntu 24.04 LTS AMI ID for ap-south-1, change accordingly
}


variable "instance_name"{
    default = "main_app_deploy"
}

variable "volume_size"{
    default = 100
}

variable "post_number"{
    default = 8000
}

variable "aws_ecr_repository_name" {
    default = "main_app_deploy"
  
}


