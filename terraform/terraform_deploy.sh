#!/bin/bash

# Copy Lambda source files to terraform directory
cp ../scrape_books.py .
cp ../scrape_books_with_categories.py .

# Deploy with Terraform
terraform init
terraform plan
terraform apply -auto-approve

echo "Deployment complete!"
echo "Bucket: $(terraform output -raw bucket_name)"

# Clean up copied files
rm scrape_books.py scrape_books_with_categories.py
