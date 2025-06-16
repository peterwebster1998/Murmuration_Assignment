provider "aws" {
  region = "us-east-1"
}

# Define necessary ports
resource "aws_security_group" "survey_app" {
  name        = "survey-app-sg"
  description = "Security group for survey application"

  # The following CIDR blocks are much too permissive but will serve for this example deployment
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance
resource "aws_instance" "survey_app" {
  ami           = "ami-0735c191cf914754d" # Ubuntu 22.04 LTS
  instance_type = "t3.micro"              # Suitable for POC workloads
  key_name      = "key_value"

  security_groups = [aws_security_group.survey_app.name]

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y docker.io docker-compose
              systemctl start docker
              systemctl enable docker
              
              # Clone fake repository
              git clone https://github.com/path/to/repo/survey-app.git
              cd survey-app
              
              # Start application
              docker-compose up -d
              EOF

  tags = {
    Name = "survey-app"
  }
}

output "public_ip" {
  value = aws_instance.survey_app.public_ip
} 