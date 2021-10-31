from datetime import date

from flask import jsonify, request

from app import app, db
from course import Course
from enrol import Enrolment
from group import Group
from user import User


class ForumThread(db.Model):
    __tablename__ = "forum_thread"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, primary_key=True)
    created_dt = db.Column(db.DateTime, nullable=False)
    updated_dt = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "created_dt": self.created_dt.strftime("%d/%m/%Y, %H:%M:%S"),
            "updated_dt": self.updated_dt.strftime("%d/%m/%Y, %H:%M:%S"),
            "title": self.title,
        }


class ForumPost(db.Model):
    __tablename__ = "forum_post"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    forum_thread_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    created_dt = db.Column(db.DateTime, nullable=False)
    updated_dt = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "forum_thread_id": self.forum_thread_id,
            "user_id": self.user_id,
            "created_dt": self.created_dt.strftime("%d/%m/%Y, %H:%M:%S"),
            "updated_dt": self.updated_dt.strftime("%d/%m/%Y, %H:%M:%S"),
            "messsage": self.message,
        }


# retrieve all forum threads & posts based on user_id in enrolment table
@app.route("/forum/thread/<int:id>", methods=["GET"])
def getSpecificThreadsAndPosts(id):
    # if learner/trainer check if he is enrolled
    enrolment = Enrolment.query.filter_by(user_id=id).first()
    if enrolment:
        threads = (
            db.session.query(ForumThread, Enrolment, ForumPost, Course)
            .filter(ForumThread.user_id == id)
            .outerjoin(Enrolment, Enrolment.user_id == ForumThread.user_id)
            .outerjoin(ForumPost, ForumPost.forum_thread_id == ForumThread.id)
            .outerjoin(Group, Group.id == Enrolment.group_id)
            .outerjoin(Course, Course.id == ForumThread.course_id)
            .all()
        )
        data = []
        for thread, enrolment, post, course in threads:
            thread = thread.json()
            thread["course_name"] = course.name
            thread["message"] = post.message
            thread["created_dt"] = post.created_dt
            thread["updated_dt"] = post.updated_dt
            data.append(thread)
        return jsonify(
            {
                "code": 200,
                "message": "Successfully retrieved forum thread",
                "data": data
            }
        ), 200
    else:
        return jsonify(
                {
                    "code": 406,
                    "message": "Sorry, You are not enrolled in any courses yet ",
                }
            ), 406


"""
Sample request body
{
    "user_id" : 1,
    "course_id" : 1,
    "created_dt" : "2021-10-15 12:00:00",
    "updated_dt" :  "2021-10-15 12:00:00",
    "title" : "Topic 1 : Engineering 101",
    "message" : "In the question it states why mary had a little lamb?"
}
"""
# create
@app.route("/forum/thread", methods=["POST"])
def createThread():
    data = request.get_json()
    try:
        forumThread = ForumThread(
            user_id=data["user_id"],
            course_id=data["course_id"],
            created_dt=date.today(),
            updated_dt=date.today(),
            title=data["title"],
        )
        db.session.add(forumThread)
        db.session.commit()
        forumThread = (
            db.session.query(ForumThread).order_by(ForumThread.id.desc()).first()
        )
        forumPost = ForumPost(
            forum_thread_id=forumThread.id,
            user_id=data["user_id"],
            created_dt=date.today(),
            updated_dt=date.today(),
            message=data["message"],
        )
        db.session.add(forumPost)
        db.session.commit()
        return jsonify(
                {
                    "code": 200,
                    "message": "Your Question has Been Successfully Created!"
                }
            ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while creating a forum thread: {e}",
                }
            ), 406


"""
Sample Request Body
{
    "title": "Engineering for Dummies 101",
    "user_id": 1 
}
"""
# Edit Thread Title
@app.route("/forum/thread/<int:id>", methods=["PUT"])
def updateThread(id):
    data = request.get_json()
    user = User.query.filter_by(id=data["user_id"]).first()
    if user:
        try:
            forum_thread = ForumThread.query.filter_by(id=id).first()
            forum_thread.title = data["title"]
            forum_thread.update_dt = date.today()
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "message": "Forum Thread Updated Successfully!"
                }
            )
        except Exception as e:
            return jsonify(
                    {
                        "code": 406,
                        "message": f"An error occurred while updating forum thread: {e}",
                    }
                ), 406
    else:
        return jsonify(
            {
                "code": 406,
                "message": f"Invalid User: {data['user_id']}"
            }
        ), 406


# Delete Forum Thread
@app.route("/forum/thread/<int:id>", methods=["DELETE"])
def deleteThread(id):
    try:
        forum_thread = ForumThread.query.filter_by(id=id).first()
        if not forum_thread:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Forum Thread not found."
                    }
                ), 406
        db.session.query(ForumPost).filter_by(forum_thread_id=id).delete()
        db.session.delete(forum_thread)
        db.session.commit()
        return jsonify(
                {
                    "code": 200,
                    "message": "Forum Thread successfully deleted"
                }
            ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while deleting forum Thread: {e}"
                }
            ), 406


"""
Sample Request Body to Update Forum
{
    "forum_thread_id" : 1,
    "user_id" :1,
    "course_id" : 1,
    "updated_dt" :  "2021-10-15 12:00:00",
    "message" : "Why did the chicken cross the road?"
}
"""
# update forum post
@app.route("/forum/post/<int:id>", methods=["PUT"])
def updatePost(id):
    data = request.get_json()
    enrolments = (
        db.session.query(Group, Enrolment, ForumPost)
        .filter(ForumPost.id == id)
        .outerjoin(Enrolment, ForumPost.user_id == Enrolment.user_id)
        .outerjoin(Group, Enrolment.group_id == Group.id)
        .all()
    )
    if enrolments:
        try:
            forum_post = ForumPost.query.filter_by(id=id).first()
            forum_post.updated_dt = date.today()
            forum_post.message = data["message"]
            db.session.commit()
            return jsonify(
                    {
                        "code": 200,
                        "message": "Forum Post Successfuly Updated!"
                    }
                ), 200
        except Exception as e:
            return jsonify(
                    {
                        "code": 406,
                        "message": f"An error occurred while creating a forum post: {e}",
                    }
                ), 406
    else:
        return jsonify(
                {
                    "code": 406,
                    "message": "You do not have permission to update the forum post!",
                }
            ), 406


# Delete forum post
@app.route("/forum/post/<int:id>", methods=["DELETE"])
def deletePost(id):
    try:
        forum_post = ForumPost.query.filter_by(id=id).first()
        if not forum_post:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Forum Post not found.",
                    }
                ), 406
        db.session.delete(forum_post)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Forum Post successfully deleted"
            }
        ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while deleting forum post: {e}",
                }
        ), 406
