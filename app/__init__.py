import os
from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
load_dotenv()

jwt = JWTManager()

# create database object
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # database connection
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

    jwt.init_app(app)

    # connect db to app
    db.init_app(app)
    migrate.init_app(app, db)

    # import models (VERY IMPORTANT for migrations)
    from app import models

    # register routes
    from app.routes import main
    app.register_blueprint(main)

    return app