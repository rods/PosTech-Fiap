#!/bin/bash

# Get bucket name from terraform output or use default
BUCKET_NAME=${1:-$(cd terraform && terraform output -raw bucket_name 2>/dev/null || echo "scrape-output")}

# Create IAM policy for S3 access
cat > lambda-s3-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
        }
    ]
}
EOF

# Create policy
aws iam create-policy \
    --policy-name LambdaS3WritePolicy \
    --policy-document file://lambda-s3-policy.json

# Get policy ARN
POLICY_ARN=$(aws iam list-policies --query "Policies[?PolicyName=='LambdaS3WritePolicy'].Arn" --output text)

# Attach policy to Lambda execution role
aws iam attach-role-policy \
    --role-name lambda-scraper-role \
    --policy-arn $POLICY_ARN

echo "IAM permissions configured for bucket: $BUCKET_NAME"
echo "Policy ARN: $POLICY_ARN"

# Clean up
rm lambda-s3-policy.json
