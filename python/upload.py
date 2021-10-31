import os
import re

import boto3
import botocore
from flask import jsonify, request
from sqlalchemy.sql.expression import all_
from werkzeug.utils import secure_filename
from course_section import CourseSection, Materials
from section_progress import SectionProgress

from app import app, db

# Upload a new file
@app.route('/upload_file', methods=["POST"])
def uploadFiles():
    try:
        if 'section_id' not in request.form:
            raise Exception('Section ID is missing from form!')
        if 'title' not in request.form:
            raise Exception('File title is missing from form!')
        if 'file' not in request.files:
            raise Exception('Please upload a file.')
        else: 
            file = request.files['file']
            filename = upload_file_to_s3(file)

        if filename[0]:
            material = Materials(
                section_id = request.form['section_id'],
                title = request.form['title'],
                material_type = "Document",
                url = f"{os.getenv('AWS_DOMAIN')}{filename[1]}"
            )
            db.session.add(material)
            db.session.commit()
            updateSectionProgress(material)  
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
        if 'section_id' not in request.form:
            raise Exception('Section ID is missing from form!')
        if 'title' not in request.form:
            raise Exception('Video title is missing from form!')
        if 'file' not in request.files:
            raise Exception('Please upload a video')
        else: 
            file = request.files['file']
            filename = upload_file_to_s3(file)

        if filename[0]:
            material = Materials(
                section_id = request.form['section_id'],
                title = request.form['title'],
                material_type = "Video",
                url = f"{os.getenv('AWS_DOMAIN')}{filename[1]}"
            )
            db.session.add(material)
            db.session.commit()
            updateSectionProgress(material)  
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


# Get File
@app.route('/file/<int:id>', methods=['GET'])
def getFile(id):
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

        return jsonify(
                {
                    "code":200,
                    "data": material.json(),
                    "message": "Material successfully retrieved."
                }
            ), 200
    except Exception as e: 
        return jsonify(
            {
                "code" : 500,
                "message" : f"Error while retrieving file: {e}",
                "data": ""
            }
        ), 500


# Update file
@app.route('/upload_file', methods=["PUT"])
def updateFile():
    try:
        if 'id' not in request.form:
            raise Exception('ID is missing from form!')
        if 'title' not in request.form:
            raise Exception('Material title is missing from form!')
        if 'file' not in request.files:
            raise Exception('Please upload a file')

        material = Materials.query.filter_by(id=request.form['id']).first()
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
        
        file = request.files['file']
        filename = upload_file_to_s3(file)

        if filename[0]:
            material.title = request.form['title']
            material.url = f"{os.getenv('AWS_DOMAIN')}{filename[1]}"
            db.session.commit()
            updateSectionProgress(material)  

            return jsonify(
                {
                    "code" : 200,
                    "message" : "Material updated successfully",
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
                "message" : f"Error while updating file: {e}",
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
        section_id = material.section_id
        all_progress = SectionProgress.query.filter_by(section_id = section_id).all()
        for progress in all_progress:
            if str(id) in progress.material:
                del progress.material[str(id)]        
        db.session.commit()
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

        # after upload file to s3 bucket, return filename of the uploaded file
        return (True, file.filename)
    except Exception as e:
        print("Something Happened: ", e)
        return (False, e)

def updateSectionProgress(material):
    all_progress = SectionProgress.query.filter_by(section_id = material.section_id).all()
    for progress in all_progress:
        progress.material[str(material.id)] = False
    db.session.commit()  