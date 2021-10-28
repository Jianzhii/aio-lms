import os
import re

import boto3
import botocore
from flask import jsonify, request
from werkzeug.utils import secure_filename
from course_section import CourseSection, Materials

from app import app, db

# Upload a new document 
@app.route('/upload_file', methods=["POST"])
def uploadFiles():
    try:
        if 'file' not in request.files:
            raise Exception('Please upload a file.')
        else: 
            file = request.files['file']
            filename = upload_file_to_s3(file)

        if filename[0]:
            material = Materials(
                section_id = request.form['id'],
                title = request.form['title'],
                material_type = "Document",
                url = f"{os.getenv('AWS_DOMAIN')}{filename[1]}"
            )
            db.session.add(material)
            db.session.commit()
            return jsonify(
                {
                    "code" : 200,
                    "message" : "File uploaded successfully",
                    "data": material.json()
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

# Upload a new video
@app.route('/upload_video', methods=["POST"])
def uploadVideo():
    try:
        if 'file' not in request.files:
            raise Exception('Please upload a video')
        else: 
            file = request.files['file']
            filename = upload_file_to_s3(file)

        if filename[0]:
            material = Materials(
                section_id = request.form['id'],
                title = request.form['title'],
                material_type = "Video",
                url = f"{os.getenv('AWS_DOMAIN')}{filename[1]}"
            )
            db.session.add(material)
            db.session.commit()
            return jsonify(
                {
                    "code" : 200,
                    "message" : "Video uploaded successfully",
                    "data": material.json()
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


# Delete material
@app.route('/material/<int:id>', methods=["DELETE"])
def deleteMaterial(id):
    try:
        material = Materials.query.filter_by(id=id).first()
        if not material: 
            return jsonify(
                {
                    "code":404,
                    "data": {
                        "id": id
                    },
                    "message": "Material not found."
                }
            ), 404

        db.session.delete(material)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Material successfully deleted"
            }
        ), 200

    except Exception as e: 
        return jsonify(
            {
                "code" : 500,
                "message" : f"Error while deleteing file: {e}",
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
