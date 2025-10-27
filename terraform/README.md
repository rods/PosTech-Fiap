# Terraform Deployment

## Deploy
```bash
cd terraform
./terraform_deploy.sh
```

## Test Functions
```bash
aws lambda invoke --function-name scrape-books response1.json
aws lambda invoke --function-name scrape-books-with-categories response2.json
```

## Destroy
```bash
terraform destroy -auto-approve
```
