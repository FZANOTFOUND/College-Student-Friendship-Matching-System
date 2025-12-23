from flask import render_template, redirect, url_for, request, flash
from . import conversation_bp
from models import User
import string
import random
import re

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_mail import Message
from datetime import datetime, timedelta
from werkzeug.datastructures import MultiDict
from werkzeug.security import generate_password_hash, check_password_hash  # 对密码进行加密
from extensions import mail, db
from models import EmailVerification, User
from decorators import *


@conversation_bp.route('/', methods=['GET'])
@my_jwt_required(limit=0, api=False)
def home():
    return render_template("conversations.html")