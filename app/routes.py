from flask import Blueprint
from flask import request
from flask_jwt_extended import create_access_token
import bcrypt
from flask_jwt_extended import jwt_required, get_jwt_identity

from .models import User, Category, Product, ProductVariant, Order, OrderItem
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

@main.route('/place-order', methods=['POST'])
@jwt_required()
def place_order():
    user_id = int(get_jwt_identity())
    data = request.json

    total_amount = 0
    order = Order(user_id=user_id, total_amount=0)

    db.session.add(order)
    db.session.flush()  # to get order.id

    for item in data['items']:
        variant = ProductVariant.query.get(item['variant_id'])

        if not variant:
            return {"error": "Variant not found"}, 404

        if variant.stock < item['quantity']:
            return {"error": "Not enough stock"}, 400

        # reduce stock
        variant.stock -= item['quantity']

        order_item = OrderItem(
            order_id=order.id,
            product_variant_id=variant.id,
            quantity=item['quantity'],
            price=variant.price
        )

        total_amount += variant.price * item['quantity']
        db.session.add(order_item)

    order.total_amount = total_amount

    db.session.commit()

    return {"message": "Order placed", "total": total_amount}