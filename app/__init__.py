from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

jwt = JWTManager()

# create database object
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = "super-secret-key"

    jwt.init_app(app)

    # database connection
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost:5432/crochet_db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # connect db to app
    db.init_app(app)
    migrate.init_app(app, db)

    # import models (VERY IMPORTANT for migrations)
    from app import models

    # register routes
    from app.routes import main
    app.register_blueprint(main)

    return app