terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.56.0"
    }
  }

  backend "s3" {
    bucket = "igvaquero-terraform-state"
    key    = "alba-y-hans-telegram/state"
    region = "eu-west-1"
  }

  required_version = "~> 1.4"
}

provider "aws" {
  region     = var.aws_region
  access_key = var.access_key
  secret_key = var.secret_key
}
