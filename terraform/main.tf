locals {
  default_security_group_name = "default"
  iam_lambda_role_name        = "hans-boda-telegram-bot"
  iam_lambda_policy_name      = "hans-boda-lambda-telegram-bot-policy"
  lambda_timeout              = 10
  tags = {
    Application = "Hans Boda"
    Environment = "prod"
  }
}

data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda_role" {
  name               = local.iam_lambda_role_name
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json

  tags = local.tags
}

data "aws_iam_policy_document" "lambda_policy_document" {
  statement {
    sid = "AWSLambdaLog"
    actions = [
      "logs:CreateLogStream",
      "logs:CreateLogGroup",
      "logs:PutLogEvents"
    ]
    resources = [
      "arn:aws:logs:${var.aws_region}:106260645150:log-group:/aws/lambda/hans-boda-telegram-bot:*:*",
      "arn:aws:logs:${var.aws_region}:106260645150:log-group:/aws/lambda/hans-boda-telegram-bot:*"
    ]
  }

  statement {
    sid = "DynamoDBStreams"
    actions = [
      "dynamodb:DescribeStream",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams"
    ]
    resources = ["arn:aws:dynamodb:${var.aws_region}:106260645150:table/${var.guests_table_name}/stream/*"]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name        = local.iam_lambda_policy_name
  description = "Hans Boda Telegram bot Lambda Policy"
  policy      = data.aws_iam_policy_document.lambda_policy_document.json
}

resource "aws_iam_role_policy_attachment" "lambda_attach_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

data "aws_dynamodb_table" "hans_boda_table" {
  name = var.guests_table_name
}

module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 4.12"

  function_name = "hans-boda-telegram-bot"
  description   = "Send a Telegram notification"
  runtime       = "python3.9"
  handler       = "lambda_function.lambda_handler"
  source_path   = "../source"
  publish       = true

  lambda_role = aws_iam_role.lambda_role.arn
  create_role = false

  timeout = local.lambda_timeout

  ephemeral_storage_size = null

  cloudwatch_logs_retention_in_days = 3

  environment_variables = {
    "HANS_BODA_TELEGRAM_TOKEN" = var.telegram_token
    "HANS_BODA_DEBUG"          = var.debug ? "true" : ""
  }

  event_source_mapping = {
    dynamodb = {
      event_source_arn                   = data.aws_dynamodb_table.hans_boda_table.stream_arn
      starting_position                  = "LATEST"
      batch_size                         = 1
      maximum_batching_window_in_seconds = 300
      filter_criteria = [
        {
          pattern = jsonencode({
            eventName : ["INSERT", "MODIFY"]
          })
        }
      ]
    }
  }

  tags                 = local.tags
  cloudwatch_logs_tags = local.tags
}
