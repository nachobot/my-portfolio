#!/c/Users/danik_000/AppData/Local/Programs/Python/Python35/

import boto3
import io # Way to have files that are only kept in meory and never put on the file systemse
import zipfile
from botocore.client import Config
import mimetypes

# Extract the files. Move them to the right bucket. Set the Content type
# Note - If you get failed to import boto3 error
# pip --version
# which Python
# Use the same version of python with which choco / pip is installed

# Configure S3 as the build bucket contents are encrypted using successes

SOURCE_BUCKET_NAME = 'portfolio.danielladsouza.com'
BUILD_BUCKET_NAME = 'portfoliobuild.danielladsouza.com'
BUILD_ARTIFACT_NAME = 'buildPortfolio.zip'
TOPIC_ARN = 'arn:aws:sns:us-east-1:145295581730:deployPortfolioTopic'

try:
    sns = boto3.resource('sns')
    topic = sns.Topic(TOPIC_ARN)

    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

    portfolio_bucket = s3.Bucket(SOURCE_BUCKET_NAME)
    build_bucket = s3.Bucket(BUILD_BUCKET_NAME)

    #In-memory binary streams are also available as BytesIO objects

    portfolio_zip = io.BytesIO()

    build_bucket.download_fileobj(BUILD_ARTIFACT_NAME, portfolio_zip)

    # Extract files
    with zipfile.ZipFile(portfolio_zip) as myzip:
        # Return a list of archive members by name.

        for nm in myzip.namelist():
            obj = myzip.open(nm)
            # Make file public with an Acl
            # Upload a file-like object to this bucket.
            # The file-like object must be in binary mode.
            portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
            portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

    topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully")
except:
    topic.publish(Subject="Portfolio Deploy Failed", Message="Portfolio was not Deployed Successfully")
    raise
