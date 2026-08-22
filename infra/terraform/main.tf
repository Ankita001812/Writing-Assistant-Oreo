resource "aws_elastic_beanstalk_application" "app" {
  name = var.app_name
}

resource "aws_elastic_beanstalk_environment" "env" {
  name                = "${var.app_name}-prod"
  application         = aws_elastic_beanstalk_application.app.name
  solution_stack_name = "64bit Amazon Linux 2023 v4.4.5 running Docker"

  # --- Cost control: single instance, no load balancer ---
  setting {
    namespace = "aws:elasticbeanstalk:environment"
    name      = "EnvironmentType"
    value     = "SingleInstance"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "InstanceType"
    value     = "t3.micro"
  }

  setting {
    namespace = "aws:autoscaling:launchconfiguration"
    name      = "IamInstanceProfile"
    value     = aws_iam_instance_profile.eb_profile.name
  }

  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_API_KEY"
    value     = var.ai_api_key
  }
  setting {
    namespace = "aws:elasticbeanstalk:application:environment"
    name      = "AI_MODEL"
    value     = "llama-3.3-70b-versatile"
  }
  setting {
    namespace = "aws:elasticbeanstalk:environment:process:default"
    name      = "HealthCheckPath"
    value     = "/health"
  }
}

resource "aws_iam_role" "eb_ec2_role" {
  name = "${var.app_name}-eb-ec2-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eb_web_tier" {
  role       = aws_iam_role.eb_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
}

resource "aws_iam_instance_profile" "eb_profile" {
  name = "${var.app_name}-eb-instance-profile"
  role = aws_iam_role.eb_ec2_role.name
}