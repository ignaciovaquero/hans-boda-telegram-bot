variable "secret_key" {
  type        = string
  description = "AWS secret key"
  sensitive   = true
}

variable "access_key" {
  type        = string
  description = "AWS access key"
}

variable "aws_region" {
  type        = string
  default     = "eu-south-2"
  description = "AWS Region for deploying resources"
}

variable "guests_table_name" {
  type        = string
  description = "The name of the DynamoDB table that holds the guest information"
  default     = "HansBodaGuests"
}

variable "telegram_token" {
  type        = string
  description = "The Telegram bot token"
  sensitive   = true
}

variable "debug" {
  type        = bool
  description = "Whether we want to activate debug logs for the lambda function or not"
  default     = false
}
