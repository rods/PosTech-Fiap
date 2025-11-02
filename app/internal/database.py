import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table("users")
table = dynamodb.Table("admin")


