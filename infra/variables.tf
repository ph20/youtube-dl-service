variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Bucket name for storing downloaded files"
  default     = "youtube-dl-service"
}
