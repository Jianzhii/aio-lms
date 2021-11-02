from flask import jsonify, request
from app import app, db
from datetime import date
from user import User


class Chat(db.Model):
    __tablename__ = "chat"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id_1 = db.Column(db.Integer, primary_key=True)
    user_id_2 = db.Column(db.Integer, primary_key=True)
    created_dt = db.Column(db.DateTime, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "user_id_1": self.user_id_1,
            "user_id_2": self.user_id_2,
            "created_dt": self.created_dt.strftime("%d/%m/%Y, %H:%M:%S"),
        }


class ChatMessages(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String, nullable=False)
    created_dt = db.Column(db.DateTime, nullable=False)

    def json(self):
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message": self.message,
            "created_dt": self.created_dt.strftime("%d/%m/%Y, %H:%M:%S"),
        }


"""
Sample Request Body
{
    "user_id_1" :1 ,
    "user_id_2" : 2,
    "message" : "hahahahah you loser"
}
"""
# Create Chat Messages
@app.route("/chat", methods=["POST"])
def createChat():
    data = request.get_json()
    data["created_dt"] = date.today()
    user1 = data["user_id_1"]  # sender
    user2 = data["user_id_2"]  # receiver
    if user1 == user2:
        return jsonify(
                {"code": 406, "data": data, "message": "Invalid User Credentials!"}
            ), 406
    exisiting_chat = Chat.query.filter_by(
        user_id_1=data["user_id_1"], user_id_2=data["user_id_2"]
    ).all()
    user1 = User.query.filter_by(id=data["user_id_1"]).first()
    user2 = User.query.filter_by(id=data["user_id_2"]).first()
    if exisiting_chat:
        return jsonify(
                {
                    "code": 406,
                    "data": data,
                    "message": f"{user1.name} has already started a chat with this {user2.name}",
                }
            ), 406
    try:
        chat = Chat(user_id_1=user1.id, user_id_2=user2.id, created_dt=date.today())
        db.session.add(chat)
        # filter by user id
        db.session.commit()
        chat = db.session.query(Chat).order_by(Chat.id.desc()).first()
        chat_message = ChatMessages(
            chat_id=chat.id,
            sender_id=user1.id,
            receiver_id=user2.id,
            created_dt=date.today(),
            message=data["message"],
        )
        db.session.add(chat_message)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Chat Successfully Created!"
            }
        ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 406,
                "message": f"The Chat Cannot be Created: {e}"
            }
        ), 406


# Get Sender chats
@app.route("/chat/sender/<int:sender_id>", methods=["GET"])
def getChatsBySenderId(sender_id):
    # Query DB
    chat_messages = ChatMessages.query.filter_by(sender_id=sender_id).all()
    if chat_messages:
        data = []
        for message in chat_messages:
            message = message.json()
            data.append(message)
        return jsonify(
            {
                "code": 200,
                "message": "Chat successfully retrieved",
                "data": data}
        ), 200
    else:
        return jsonify(
            {
                "code": 406,
                "data": f"Invalid Sender ID: {sender_id}"
            }
        ), 406


# Get receiver chats
@app.route("/chat/receiver/<int:receiver_id>", methods=["GET"])
def getChatsByReceiverId(receiver_id):
    # Query DB
    chat_messages = ChatMessages.query.filter_by(sender_id=receiver_id).all()
    if chat_messages:
        data = []
        for message in chat_messages:
            message = message.json()
            data.append(message)
        return jsonify(
            {
                "code": 200,
                "message": "Chat successfully retrieved",
                "data": data
            }
        ), 200
    else:
        return jsonify(
            {
                "code": 406,
                "data": f"Invalid Sender ID: {receiver_id}"
            }
        ), 406


# edit messages
"""
Sample Request Body
{
    "messages":"bro are you okay?",
    "user_id": 1
}
"""
@app.route("/chat/update/<int:id>", methods=["PUT"])
def updateMessage(id):
    data = request.get_json()
    chat_message = ChatMessages.query.filter_by(id=id).first()
    if chat_message:
        try:
            if chat_message.sender_id == data["user_id"]:
                chat_message.message = data["messages"]
                db.session.commit()
                return jsonify(
                    {
                        "code": 200,
                        "message": "Message update success"
                    }
                ), 200
            else:
                return jsonify(
                    {
                        "code": 406,
                        "message": f"Invalid User Credentials! : {data['user_id']}",
                    }
                )
        except Exception as e:
            return jsonify(
                    {
                        "code": 406,
                        "message": f"An error occurred while approving request: {e}",
                    }
                ), 406
    else:
        return jsonify(
            {
                "code": 406,
                "message": f"Invalid Chat Message ${id}"
            }
        ), 406


@app.route("/chat/delete/<int:id>", methods=["DELETE"])
def deleteChat(id):
    try:
        chat = Chat.query.filter_by(id=id).first()
        if not chat:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": "Chat not found."}
                ), 406
        db.session.query(ChatMessages).filter_by(chat_id=id).delete()
        db.session.delete(chat)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Chat successfully deleted"
            }
        ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while deleting Chat : {e}"
                }
        ), 406


@app.route("/chat/delete/message/<int:id>", methods=["DELETE"])
def deleteMessage(id):
    try:
        chat_message = ChatMessages.query.filter_by(id=id).first()
        if not chat_message:
            return jsonify(
                    {
                        "code": 406,
                        "data": {"id": id},
                        "message": f"message not found {id}.",
                    }
            ), 406
        db.session.delete(chat_message)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "message": "Chat successfully deleted"
            }
        ), 200
    except Exception as e:
        return jsonify(
                {
                    "code": 406,
                    "message": f"An error occurred while deleting Chat : {e}"
                }
        ), 406
