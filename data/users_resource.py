from flask_restful import Resource
from . import db_session
from .users import User
from flask import abort, jsonify
from .parse_user import parser
from werkzeug.security import generate_password_hash


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found.")
    return session


class UsersResource(Resource):
    def get(self, user_id):
        session = abort_if_user_not_found(user_id)
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('email', 'password', 'surname', 'name', 'age', 'position', 'speciality', 'address'))})

    def delete(self, user_id):
        session = abort_if_user_not_found(user_id)
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, user_id):
        return jsonify({'message': 'No editing function in RESTFUL-API. (Дело в том, что \
спецификация HTML позволяет создавать формы, отправляющие только GET- или POST-запросы.)'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict() for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User()
        user.email = args['email']
        user.hashed_password = generate_password_hash(args['password'])
        user.surname = args['surname']
        user.name = args['name']
        user.age = args['age']
        user.position = args['position']
        user.speciality = args['speciality']
        user.address = args['address']
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
