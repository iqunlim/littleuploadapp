Environment variables:
- S3_BUCKET (required) the name of the bucket (without s3:// or any other protocol).
- S3_REGION (default: us-east-2) the region the bucket is located in.
- MAX_SIZE (default 20) the maximum upload size in megabytes that the application allows.
- PORT (default 5000) the port that the flask application will run on.

To use:
- `python3 -m pip install -r requirements.txt`
- `./run.sh`

# 
You can find a container for use here:
https://hub.docker.com/repository/docker/iqunlim/littleupload
