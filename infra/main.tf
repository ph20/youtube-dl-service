provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

resource "aws_dynamodb_table" "youtube_dl" {
  name           = "videosInfo"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "uuid"
  range_key      = "url"

  attribute {
    name = "uuid"
    type = "S"
  }

  attribute {
    name = "url"
    type = "S"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }
}
