import boto3
import os
import json
import request_filtered_stream
from base64 import b64decode
from datetime import datetime

s3_client = boto3.client('s3')
# Get the encrypted bearer token from environment variable, this can be set on lambda function itself
ENCRYPTED = os.environ['BEARER_TOKEN']
# Decrypt bearer token
bearer_token = boto3.client('kms').decrypt(
    CiphertextBlob=b64decode(ENCRYPTED),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext'].decode('utf-8')
# Get a header from using the bearer token as this will be frequently used by many parts of the program.
headers = request_filtered_stream.create_headers(bearer_token)
# Save all current rules from twitter to rules variable in case we want to delete or show all rules later.
rules = request_filtered_stream.get_rules(headers)


# Main lambda function handler, this function name can be different but should be the same as the name of the handler
# you created for your lambda function.
def lambda_handler(request, context):
    # to test locally on lambda function page comment the following line,
    # otherwise it needs to be there for lambda to correct process data from api gateway.
    event = json.loads(request["body"])
    # The following line will delete all rules current associate with your twitter developer's account.
    # Uncomment it when necessary for testing
    # request_filtered_stream.delete_all_rules(headers, rules)

    # In a REST request, the body should have at least two value paris, event and tag while tag can be empty.
    new_rule = request_filtered_stream.set_rules(headers, request['event'], request['tag'])
    # print(new_rule)
    # This is for managing who sends the request, can be empty but do not included this in the request to Twitter
    event_owner = request['owner']
    # Error handling and returning status code so web server sending the request can show user a submission result
    if new_rule['meta']['summary']['invalid']:
        response = {"isBase64Encoded": False, "statusCode": 400, "headers": {"status": "Failed!"},
                    "body": str(new_rule['errors'])}
    else:
        response = {"isBase64Encoded": False, "statusCode": 201, "headers": {"status": "Success!"},
                    "body": str(new_rule['data'])}
        stream_id = new_rule['data'][0]['id']
        # Write to bucket a few data about the request once it is accepted by twitter. This can be used to keep track
        # who sent what requests and later on this data can be cross-referenced with rules to match job status
        write_bucket(stream_id, event_owner, str(new_rule))
    return response


# Function to take care sending data to S3 bucket about the request, not for streaming
def write_bucket(filename, owner, data):
    bucket_name = ####YOUR_S3_BUCKET_HERE!!!!#####
    lambda_path = '/tmp' + filename
    s3_path = 'research_owners/' + owner + '/' + str(datetime.now().year) + '/' + str(
        datetime.now().month) + '/' + filename

    s3 = boto3.resource("s3")
    s3.Bucket(bucket_name).put_object(Key=s3_path, Body=data)


if __name__ == "__main__":
    lambda_handler('a', 'b')
