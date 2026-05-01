from flask import Blueprint
from flask import request
from flask_jwt_extended import create_access_token
import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import User, Category, Product, ProductVariant
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

# @main.route('/add-product', methods=['POST'])
# @jwt_required()
# def add_product():
#     data = request.json

#     category = Category.query.filter_by(name=data['category']).first()

#     if not category:
#         return {"error": "Category not found"}, 404

#     product = Product(
#         name=data['name'],
#         description=data.get('description'),
#         base_price=data['base_price'],
#         category_id=category.id
#     )

#     db.session.add(product)
#     db.session.commit()

#     return {"message": "Product added"}


@main.route('/add-product', methods=['POST'])
@jwt_required()
def add_product():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    # 🔒 ADMIN CHECK
    if user.role != "admin":
        return {"error": "Only admin can add products"}, 403

    data = request.json

    category = Category.query.filter(
        Category.name.ilike(data['category'].strip())
    ).first()

    if not category:
        return {"error": "Category not found"}, 404

    product = Product(
        name=data['name'],
        description=data.get('description'),
        base_price=data['base_price'],
        category_id=category.id
    )

    db.session.add(product)
    db.session.commit()

    return {"message": "Product added"}

@main.route('/add-variant', methods=['POST'])
@jwt_required()
def add_variant():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if user.role != "admin":
        return {"error": "Only admin can add variants"}, 403
    
    data = request.json

    product = Product.query.filter_by(name=data['product']).first()

    if not product:
        return {"error": "Product not found"}, 404

    variant = ProductVariant(
        product_id=product.id,
        color=data['color'],
        stock=data['stock'],
        price=data['price']
    )

    db.session.add(variant)
    db.session.commit()

    return {"message": "Variant added"}

@main.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()

    result = []

    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "category": p.category.name,
            "base_price": p.base_price
        })

    return result