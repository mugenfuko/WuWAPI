from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, ValidationError, fields

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class CharacterModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rarity = db.Column(db.Integer, nullable=False)
    element = db.Column(db.String(100), nullable=False)
    weapon = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Character(name= {name}, rarity= {rarity}, element= {element}, weapon= {weapon})"

characters = {
    "1": {
        "name": "Cartethyia",
        "rarity": 5,
        "element": "aero",
        "weapon": "sword"
        }
}

class CharacterSchema(Schema):
    name = fields.Str(required=True)
    rarity = fields.Int(required=True)
    element = fields.Str(required=True)
    weapon = fields.Str(required=True)

schema = CharacterSchema()

def abort_if_character_doesnt_exist(char_id):
    if char_id not in characters:
        abort(404, message="Character not found")

def abort_if_character_exists(char_id):
    if char_id in characters:
        abort(404, message="Character already exists")

class Character(Resource):

    def get(self, char_id):
        abort_if_character_doesnt_exist(char_id)
        return characters[char_id], 200

    def put(self, char_id):
        abort_if_character_exists(char_id)
        json_data = request.get_json()
        try:
            data = schema.load(json_data)
        except ValidationError as err:
            return err.messages, 422
        result = schema.dump(data)
        characters[char_id] = result
        return characters[char_id], 201

    def delete(self, char_id):
        abort_if_character_doesnt_exist(char_id)
        del characters[char_id]
        return "", 204

class CharacterList(Resource):
    def get(self):
        return characters

api.add_resource(CharacterList, "/characters")
api.add_resource(Character, "/characters/<char_id>")

if __name__ == "__main__":
    app.run(debug=True)