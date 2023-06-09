import boto3
from decouple import config

AWS_ACCESS_KEY_ID     = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
REGION_NAME           = config("REGION_NAME")
BUCKET_NAME           = config("BUCKET_NAME")
API_KEY               = config("API_KEY")
API_SECRET            = config("API_SECRET")
ACCESS_TOKEN          = config("ACCESS_TOKEN")

client = boto3.client(
    'dynamodb',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = REGION_NAME,
)
resource = boto3.resource(
    'dynamodb',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = REGION_NAME,
)

s3Client = boto3.client(
    's3',
    aws_access_key_id     = AWS_ACCESS_KEY_ID,    
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = REGION_NAME,
)