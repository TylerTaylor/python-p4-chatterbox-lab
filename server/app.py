from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# GET returns an array of all messages as JSON, ordered by created_at in ascending order.
# POST creates a new message with a body and username from params, and returns the newly created post as JSON.
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at).all()
        messages_serialized = [message.to_dict() for message in messages]

        response = make_response(messages_serialized, 200)
        return response

    elif request.method == 'POST':
        data = request.get_json()
        new_message = Message(
            body = data["body"],
            username = data["username"]
        )

        db.session.add(new_message)
        db.session.commit()

        new_message_dict = new_message.to_dict()
        response = make_response(new_message_dict, 201)
        return response

# PATCH updates the body of the message using params, and returns the updated message as JSON.
# DELETE deletes the message from the db
@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    # can fetch the object at this top level instead of repeating per method
    message = Message.query.filter_by(id = id).first()

    if request.method == 'PATCH':
        
        for attr in request.get_json():
            setattr(message, attr, request.get_json()[attr])

        db.session.add(message)
        db.session.commit()

        return make_response(message.to_dict(), 200)
    
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        return make_response({ "message": "Message deleted" }, 200)

if __name__ == '__main__':
    app.run(port=5555)
