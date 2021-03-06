import traceback
from base64 import b64decode, b64encode
import boto3
import requests
import os
import json
import datetime
import logging
from botocore.exceptions import ClientError

# Below code will take care decrypting the bearer token that is saved as an environment variable in the OS.
# You may need to manually created an encrypted bearer token using the similar code below but to encrypt. 
key_id = ####YOUR KMS key ARN here#####
encrypted = os.environ['BEARER_TOKEN'].encode('utf-8')
bearer_token = boto3.client('kms').decrypt(
    KeyId=key_id,
    EncryptionAlgorithm='SYMMETRIC_DEFAULT',
    CiphertextBlob=b64decode(encrypted),
    EncryptionContext={####REfer to AWS KMS doc for this field, optional but highly recommended to have it for better security####}
)['Plaintext'].decode('utf-8')


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers
        

# This is the streamer, in the case of disconnection, it shall reconnect again. Few data may be lost during reconnection
def get_stream(headers):
    # Tone down your additonal fields here, you may not need all these
    additional_fields = "tweet.fields=attachments%2Cauthor_id%2Ccontext_annotations%2Cconversation_id%2Ccreated_at%2Centities%2Cgeo%2Cid%2Cin_reply_to_user_id%2Clang%2Cpublic_metrics%2Cpossibly_sensitive%2Creferenced_tweets%2Creply_settings%2Csource%2Ctext%2Cwithheld&user.fields=created_at%2Cdescription%2Centities%2Cid%2Clocation%2Cname%2Cpinned_tweet_id%2Cprofile_image_url%2Cprotected%2Cpublic_metrics%2Curl%2Cusername%2Cverified%2Cwithheld&expansions=attachments.poll_ids%2Cattachments.media_keys%2Cauthor_id%2Centities.mentions.username%2Cgeo.place_id%2Cin_reply_to_user_id%2Creferenced_tweets.id%2Creferenced_tweets.id.author_id"
    kinesis_name = ###Your kinesis stream name####
    kinesis_client = boto3.client('kinesis')
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?" + additional_fields, headers=headers, stream=True,
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        try:
            kinesis_client.put_record(StreamName=kinesis_name,
                                      Data=response_line,
                                      PartitionKey="Twitter"
                                      )
        except ClientError as e:
            logging.error(e)
            initiator()


def initiator():
    headers = create_headers(bearer_token)
    get_stream(headers)


if __name__ == "__main__":
    initiator()
