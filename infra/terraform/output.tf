output "application_url" {
  description = "Public URL of the deployed app"
  value       = "http://${aws_elastic_beanstalk_environment.env.endpoint_url}"
}