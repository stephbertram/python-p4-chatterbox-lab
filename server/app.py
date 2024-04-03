from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.json.compact = False

cors = CORS(app)
migrate = Migrate(app, db)
db.init_app(app)

# whitelisting GET & POST
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # messages = []
        # don't need the .all() in Message.query.all() to create a list because creating list above
        # for message in Message.query:
        #     message_dict = message.to_dict()
        #     messages.append(message_dict)

        messages = [message.to_dict() for message in Message.query.order_by("created_at")]
        response = make_response(messages, 200)
        return response
    elif request.method == 'POST':
        new_message = Message(
            # first get json representation of data, then can .get
            # in the future when have a lot of attributes will want to spread the data
            body=request.get_json().get("body", "Body of message was not present"),
            username=request.get_json().get("username"),
        )
        db.session.add(new_message)
        db.session.commit()

        response = make_response(new_message.to_dict(), 201)
        return response
    
        # else:
        # data = request.json
        # new_message = Message(
        #     username=data.get("username"), 
        #     body=data.get("body")
        # )
        # db.session.add(new_message)
        # db.session.commit()
        # return new_message.to_dict(), 201


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = db.session.get(Message, id)
    if message:
        if request.method == 'DELETE':
        
                db.session.delete(message)
                db.session.commit()
                # don't send anything back because the delete worked
                return "", 204
        else:
            if message:
                data = request.json
                # get is safest way to extract from a dictionary, can add a default
                for attr, value in data.items():
                    #setattr(object, attribute, value)
                    setattr(message, attr, value) #! model validation always kick in when resetting attribute value
                db.session.commit() #! db constraints
                return message.to_dict(), 200
    else:
        return {"error": f"Message with id {id} not found."}, 404




# Always run in debug! python app.py
if __name__ == '__main__':
    app.run(port=5555, debug=True)

# import ipdb; ipdb.set_trace()