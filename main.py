from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, exc
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

    #def __repr__(self):
    #    return f"Character(name= {self.name}

class CharacterSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    rarity = fields.Int(required=True)
    element = fields.Str(required=True)
    weapon = fields.Str(required=True)

schema = CharacterSchema()

class Character(Resource):

    def serialize_request(self, request):
        try:
            raw_data = schema.load(request.get_json())
        except ValidationError as err:
            return err.messages, 422
        return schema.dump(raw_data)
    
    def post(self, char_id):
        char_data = self.serialize_request(request)
        character = CharacterModel(
            id = int(char_id),
            name = char_data["name"],
            rarity = char_data["rarity"],
            element = char_data["element"],
            weapon = char_data["weapon"]
        )
        try:
            db.session.add(character)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
        return char_data, 201

    def get(self, char_id):
        try:
            char_id = int(char_id)
        except ValueError:
            try:
                character = schema.dump(
                    db.session.execute(
                        db.select(CharacterModel).where(CharacterModel.name == char_id.lower().capitalize())
                    ).scalars().one()
                )
            except exc.NoResultFound:
                return {}, 404
            return character, 200

        character = schema.dump(db.session.get(CharacterModel, char_id))
        if not character:
            return {}, 404
        return character, 200

    def put(self, char_id):
        char_data = self.serialize_request(request)
        character = db.session.get(CharacterModel, char_id)
        if not character:
            return {}, 404
        character.name = char_data["name"]
        character.rarity = char_data["rarity"]
        character.element = char_data["element"]
        character.weapon = char_data["weapon"]
        db.session.commit()
        return {}, 200

    def patch(self, char_id):
        return self.put(char_id)

    def delete(self, char_id):
        character = db.session.get(CharacterModel, char_id)
        if not character:
            return {}, 404
        db.session.delete(character)
        db.session.commit()
        return {}, 204

class CharacterList(Resource):
    def get(self):
        character_list = {}
        all_characters = db.session.execute(
            db.select(CharacterModel).order_by(CharacterModel.id)
        ).scalars().all()
        for char in all_characters:
            char = schema.dump(char)
            char_id = char["id"]
            del char["id"]
            character_list[char_id] = char
        return character_list

api.add_resource(CharacterList, "/characters")
api.add_resource(Character, "/characters/<char_id>")

with app.app_context():
    db.create_all()

characters_arr_example = [
    {
        "id": 1,
        "name": "Cartethyia",
        "rarity": 5,
        "element": "aero",
        "weapon": "sword"
    }
]

if __name__ == "__main__":
    app.run(debug=True)
