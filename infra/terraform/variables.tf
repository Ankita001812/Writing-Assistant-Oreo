variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-southeast-2"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "ai-writing-assistant"
}

variable "ai_api_key" {
  description = "Secret API key for the AI provider"
  type        = string
  sensitive   = true   # Terraform will hide this in logs/plan output
}