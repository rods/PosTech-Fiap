import boto3
import csv
import json
from io import StringIO
from decimal import Decimal

def lambda_handler(event, context):
    """
    Load CSV data from S3 to DynamoDB.
    
    Event format:
    {
        "bucket": "your-bucket-name",
        "file": "books.csv"
    }
    """
    
    try:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        table = dynamodb.Table('books')
        
        bucket = event.get('bucket')
        file_key = event.get('file')
        
        if not bucket or not file_key:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing parameters',
                    'message': 'Provide bucket and file parameters'
                })
            }
        
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')
        
        csv_reader = csv.DictReader(StringIO(csv_content))
        
        loaded_count = 0
        skipped_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, 1):
            try:
                if not all(field in row for field in ['id', 'title', 'price', 'rating', 'availability', 'category']):
                    errors.append(f"Row {row_num}: Missing fields")
                    continue
                
                item = {
                    'id': int(row['id']),
                    'title': row['title'].strip(),
                    'price': Decimal(str(row['price'])),
                    'rating': int(row['rating']),
                    'availability': row['availability'].strip(),
                    'category': row['category'].strip()
                }
                
                table.put_item(
                    Item=item,
                    ConditionExpression='attribute_not_exists(id)'
                )
                
                loaded_count += 1
                print(f"Loaded row {row_num}: {item['title']}")
                
            except table.meta.client.exceptions.ConditionalCheckFailedException:
                skipped_count += 1
                print(f"Skipped row {row_num}: ID {row['id']} exists")
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                print(f"Error row {row_num}: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing completed',
                'loaded': loaded_count,
                'skipped': skipped_count,
                'errors': len(errors)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
