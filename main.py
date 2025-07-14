from flask import Flask, request
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from marshmallow import Schema, ValidationError, fields

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class CharacterModel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    rarity: Mapped[int] = mapped_column(nullable=False)
    element: Mapped[str] = mapped_column(nullable=False)
    weapon: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"Character(name= {self.name}"

class CharacterSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    rarity = fields.Int(required=True)
    element = fields.Str(required=True)
    weapon = fields.Str(required=True)

schema = CharacterSchema()

class Character(Resource):

    def get(self, char_id):
        character = schema.dump(db.session.get(CharacterModel, char_id))
        return character, 200

    def post(self, char_id):
        try:
            data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 422
        result = schema.dump(data)
        character = CharacterModel(
            id = int(char_id),
            name = result["name"],
            rarity = result["rarity"],
            element = result["element"],
            weapon = result["weapon"]
        )
        db.session.add(character)
        db.session.commit()
        return result, 201

    def delete(self, char_id):
        db.session.delete(db.session.get(CharacterModel, char_id))
        db.session.commit()
        return {}, 204

class CharacterList(Resource):
    def get(self):
        return characters

api.add_resource(CharacterList, "/characters")
api.add_resource(Character, "/characters/<char_id>")

with app.app_context():
    db.create_all()

characters = {
    "1": {
        "id": 1,
        "name": "Cartethyia",
        "rarity": 5,
        "element": "aero",
        "weapon": "sword"
        }
}

if __name__ == "__main__":
    app.run(debug=True)
