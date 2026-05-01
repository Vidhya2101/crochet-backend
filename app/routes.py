from flask import Blueprint
from flask import request
from flask_jwt_extended import create_access_token
import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import User
from . import db

# create blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return {"message": "Backend is running 🚀"}

@main.route('/register', methods=['POST'])
def register():
    data = request.json

    hashed_pw = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_pw.decode('utf-8')
    )

    db.session.add(user)
    db.session.commit()

    return {"message": "User registered"}

@main.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return {"error": "User not found"}, 404

    if not bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        return {"error": "Wrong password"}, 401

    token = create_access_token(identity=str(user.id))

    return {"token": token}

#protected route
@main.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    return {"message": f"Welcome user {user.name}"}