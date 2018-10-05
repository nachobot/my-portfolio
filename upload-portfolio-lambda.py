
import json
import boto3
from botocore.client import Config
import io  # StringIO and BytesIO from Python2
import zipfile
import mimetypes

def lambda_handler(event, context):

    # Used when we invoke lambda function manually
    location = {
        "bucketName": 'portfoliobuild.danielladsouza.com',
        "objectKey": 'buildPortfolio.zip'
    }
    # https://docs.aws.amazon.com/codepipeline/latest/userguide/actions-invoke-lambda-function.html
    try:
        job = event.get("CodePipeline.job")

        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]

        print("Building portfolio from " + str(location))

        sns = boto3.resource('sns')
        topic = sns.Topic('arn:aws:sns:us-east-1:145295581730:deployPortfolioTopic')

        # Files stored in the Build Bucket are encrypted AWS KMS
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

        # Source code bucket
        portfolio_bucket = s3.Bucket('portfolio.danielladsouza.com')

        # Destination Build bucket
        build_bucket = s3.Bucket(location['bucketName'])


        # Read the file directly into memory
        # IO in memory file - portfolio_zip

        portfolio_zip = io.BytesIO()

        # Download the zipped file to the object
        build_bucket.download_fileobj(location['objectKey'], portfolio_zip)

        # Extract, upload, set ACL
        with zipfile.ZipFile(portfolio_zip) as myZip:
            for name in myZip.namelist():
                obj = myZip.open(name)
                print(mimetypes.guess_type(name)[0])
                portfolio_bucket.upload_fileobj(obj, name,
                 ExtraArgs={'ContentType': mimetypes.guess_type(name)[0]})
                portfolio_bucket.Object(name).Acl().put(ACL='public-read')
                
        topic.publish(Subject="Deployment Status Update", Message="Portfolio deployed successfully")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
        print("Job Done!")
    except:
        topic.publish(Subject="Deployment Failed", Message="Portfolio was not deployed successfully")
        raise

    return 'Hello from Lambda'
