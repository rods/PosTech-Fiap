terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "scrape_output" {
  bucket = "scrape-output-${random_string.suffix.result}"
}

resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda-scraper-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_role.name
}

resource "aws_iam_role_policy" "s3_access" {
  name = "s3-access"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["s3:PutObject"]
        Resource = "${aws_s3_bucket.scrape_output.arn}/*"
      }
    ]
  })
}

data "archive_file" "scrape_books" {
  type        = "zip"
  source_file = "scrape_books.py"
  output_path = "scrape_books.zip"
}

data "archive_file" "scrape_books_with_categories" {
  type        = "zip"
  source_file = "scrape_books_with_categories.py"
  output_path = "scrape_books_with_categories.zip"
}

resource "aws_lambda_function" "scrape_books" {
  filename         = "scrape_books.zip"
  function_name    = "scrape-books"
  role            = aws_iam_role.lambda_role.arn
  handler         = "scrape_books.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  source_code_hash = data.archive_file.scrape_books.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.scrape_output.bucket
    }
  }
}

resource "aws_lambda_function" "scrape_books_with_categories" {
  filename         = "scrape_books_with_categories.zip"
  function_name    = "scrape-books-with-categories"
  role            = aws_iam_role.lambda_role.arn
  handler         = "scrape_books_with_categories.lambda_handler"
  runtime         = "python3.9"
  timeout         = 300
  source_code_hash = data.archive_file.scrape_books_with_categories.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.scrape_output.bucket
    }
  }
}
