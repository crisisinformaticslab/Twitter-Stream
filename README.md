# Twitter-Stream
Usage:

1. Import lambda_function.py and request_filtered_stream.py. You may need to fix the missing modules, this can be fixed by uploading a completed python project with missing module installed.

2. Put streamer.py, twitter-stream-initiator.sh and twitter-stream.service to your favorite Linux distribution that has systemd. Use twitter-stream-initiator.sh and twitter-stream.service to create a new service that can be enabled an started whenever the system is reboot. 

3. The IAM role/user for the EC2 instance needs the following permissions(Not my best effort to trimming permissions):
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt",
                "kms:Encrypt",
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "firehose:*",
                "kinesis:*",
            ],
            "Resource": "*"
        }
    ]
}
