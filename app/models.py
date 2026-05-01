from . import db

# 👤 User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default="customer")


# 🗂️ Category
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    products = db.relationship('Product', backref='category', lazy=True)


# 🧶 Product
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    base_price = db.Column(db.Float)

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    variants = db.relationship('ProductVariant', backref='product', lazy=True)


# 🎨 Product Variant (color + stock)
class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))

    color = db.Column(db.String(50))
    stock = db.Column(db.Integer, default=0)
    price = db.Column(db.Float)