import config
import models
from account import account_bp, api_account_bp
from errors import errors_bp
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_login import current_user
from extensions import db, mail, jwt, bcrypt, cors
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import timedelta

# load env
load_dotenv()

# create app

app = Flask(__name__)

app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

# register extensions after config
db.init_app(app)
mail.init_app(app)
jwt.init_app(app)
cors._options = {"supports_credentials": True,
                 "origins": [
                     r"http://localhost:\d+",
                     r"http://127\.0\.0\.1:\d+",
                     r"http://192\.168\.\d+\.\d+:\d+",
                     r"http://10\.\d+\.\d+\.\d+:\d+",
                 ]}
cors.init_app(app)
bcrypt.init_app(app)
Migrate(app, db)

# 注册蓝图
app.register_blueprint(account_bp, url_prefix='/account')
app.register_blueprint(api_account_bp, url_prefix='/api/account')
app.register_blueprint(errors_bp)


@app.route('/')
def index():
    return render_template('index.html')


# CLI helper to create tables quickly
@app.cli.command('init-db')
def init_db():
    """Quick create tables (for development). In production use migrations."""
    with app.app_context():
        db.create_all()
        print("DB initialized (db.create_all()).")


if __name__ == '__main__':
    app.run(host=config.FLASK_RUN_HOST, port=config.FLASK_RUN_PORT, debug=config.FLASK_DEBUG)
