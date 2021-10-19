import os

import boto3
import botocore
from flask import jsonify, request
from werkzeug.utils import secure_filename

from app import app, db


@app.route('/upload', methods=["POST"])
def upload():
    try:
        if 'file' not in request.files:
            print('no files?')
        else: 
            file = request.files['file']
            filename = upload_file_to_s3(file)
        if filename[0]:
            return jsonify(
                {
                    "code" : 200,
                    "message" : "File uploaded successfully",
                    "data": {
                        "url_link": f"{os.getenv('AWS_DOMAIN')}{filename[1]}"
                    }
                }
            ), 200

        return jsonify(
            {
                "code" : 500,
                "message" : f"Error while uploading file: {filename[1]}",
                "data": ""
            }
        ), 500
	
    except Exception as e: 
        return jsonify(
            {
                "code" : 500,
                "message" : f"Error while uploading file: {e}",
                "data": ""
            }
        ), 500


def upload_file_to_s3(file, acl="public-read"):
    filename = secure_filename(file.filename)
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        s3.upload_fileobj(
            file,
            os.getenv("AWS_BUCKET_NAME"),
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return (False, e)
    

    # after upload file to s3 bucket, return filename of the uploaded file
    return (True, file.filename)
