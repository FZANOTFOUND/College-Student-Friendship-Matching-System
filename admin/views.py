from flask import render_template, redirect, url_for, request, flash
from . import admin_bp
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
@admin_bp.route('/', methods=['GET', 'POST'])
@my_jwt_required(limit=1, api=False)
def root():
    return render_template('admin/root.html')


@admin_bp.route('/info', methods=['GET', 'POST'])
@my_jwt_required(limit=1, api=False)
def info():
    return render_template('admin/info.html')

@admin_bp.route('/users', methods=['GET', 'POST'])
@my_jwt_required(limit=1, api=False)
def users():
    return render_template('admin/users.html')


@admin_bp.route('/conversations', methods=['GET', 'POST'])
@my_jwt_required(limit=1, api=False)
def conversations():
    return render_template('admin/conversations.html')