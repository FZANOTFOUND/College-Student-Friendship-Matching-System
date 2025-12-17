from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
mail = Mail()
jwt = JWTManager()
cors = CORS()
bcrypt = Bcrypt()