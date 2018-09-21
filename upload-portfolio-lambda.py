import boto3
from botocore.client import Config
import io  # Python3
import zipfile
import mimetypes

# Files stored in the Build Bucket are encrypted AWS KMS
s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

# Source code bucket
portfolio_bucket = s3.Bucket('portfolio.danielladsouza.com')

# Destination Build bucket
build_bucket = s3.Bucket('portfoliobuild.danielladsouza.com')

# Read the file directly into memory
# IO in memory file - portfolio_zip

portfolio_zip = io.BytesIO()

# Download the zipped file to the object
build_bucket.download_fileobj('buildPortfolio.zip', portfolio_zip)

# Extract, upload, set ACL
with zipfile.ZipFile(portfolio_zip) as myZip:
    for item in myZip.namelist():
        obj = myZip.open(item)
        portfolio_bucket.upload_fileobj(obj, item,
         ExtraArgs={'ContentType': mimetypes.guess_type(item)[0]})
        portfolio_bucket.Object(item).Acl().put(ACL='public-read')
