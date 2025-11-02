# Lambda Testing Guide

## Test Event

```json
{
  "bucket": "your-bucket-name",
  "file": "books.csv"
}
```

## Response

```json
{
  "statusCode": 200,
  "body": "{\"message\": \"Processing completed\", \"loaded\": 25, \"skipped\": 0, \"errors\": 0}"
}
```

## CSV Format

Required columns: id, title, price, rating, availability, category

## How to Test in Lambda Console

### Step 1: Deploy the Function
1. Copy the updated `load_to_dynamodb.py` code
2. Create or update your Lambda function
3. Ensure the function has DynamoDB permissions

### Step 2: Configure Test Events
1. In Lambda console, click "Test" button
2. Select "Create new test event"
3. Choose "Custom event template"
4. Copy one of the test events above
5. Give it a descriptive name (e.g., "TestTableConnection")
6. Save the test event

### Step 3: Run Tests
1. Select your test event from dropdown
2. Click "Test" button
3. Check the execution results and logs

### Step 4: Verify Results
- For table connection: Check the response shows table info
- For sample data: Verify books are added to DynamoDB
- For clear data: Confirm test books are removed
- Check CloudWatch logs for detailed execution info

## Testing Workflow

**Recommended testing sequence**:

1. **Test Connection** → Verify Lambda can connect to DynamoDB
2. **Load Sample Data** → Add test books to verify write operations
3. **Test Your API** → Use the sample books to test your Books API
4. **Clear Test Data** → Clean up when done testing
5. **S3 Event Test** → Test production CSV processing (optional)

## Monitoring and Debugging

### CloudWatch Logs
- All operations are logged with ✅ ❌ ⚠️ emojis for easy identification
- Check logs for detailed execution information
- Error messages include specific details for debugging

### DynamoDB Console
- Verify data in DynamoDB console after loading
- Check item counts and data integrity
- Use DynamoDB queries to inspect loaded data

### Common Issues

**Permission Errors**:
- Ensure Lambda execution role has DynamoDB permissions
- Check IAM policies for `dynamodb:PutItem`, `dynamodb:DeleteItem`, `dynamodb:DescribeTable`

**Table Not Found**:
- Verify table name is "Books" (case-sensitive)
- Check region configuration (us-east-2)
- Ensure table exists in the correct AWS account/region

**Data Format Errors**:
- Check CSV format matches expected columns
- Verify data types (id and rating must be integers)
- Ensure price values are valid numbers

## Integration with Books API

After loading sample data, you can test the Books API endpoints:

```bash
# Get all books (should include test books)
curl http://localhost:8000/api/v1/books

# Get specific test book
curl http://localhost:8000/api/v1/books/9001

# Search by category
curl "http://localhost:8000/api/v1/books/search?category=Technology"
```

## Production Use

For production S3 events, the function automatically:
- Processes CSV files uploaded to S3
- Handles duplicate detection (skips existing IDs)
- Provides detailed success/error reporting
- Logs all operations for monitoring

The test mode functionality doesn't interfere with production operations.