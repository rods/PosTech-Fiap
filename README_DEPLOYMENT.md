# Lambda Deployment Guide

## Quick Deploy

1. **Create packages:**
   ```bash
   ./deploy.sh
   ```

2. **Deploy infrastructure:**
   ```bash
   aws cloudformation deploy --template-file cloudformation.yaml --stack-name book-scraper --capabilities CAPABILITY_IAM
   ```

3. **Update Lambda code:**
   ```bash
   aws lambda update-function-code --function-name scrape-books --zip-file fileb://lambda-packages/scrape_books.zip
   aws lambda update-function-code --function-name scrape-books-with-categories --zip-file fileb://lambda-packages/scrape_books_with_categories.zip
   ```

## Test Functions

```bash
aws lambda invoke --function-name scrape-books response1.json
aws lambda invoke --function-name scrape-books-with-categories response2.json
```

## Output

CSV files will be saved to S3 bucket `scrape-output` with timestamps.
