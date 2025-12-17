from flask import render_template, redirect, url_for, request, flash
from . import account_bp, api_account_bp
from models import User
from .forms import RegisterForm, LoginForm
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


@account_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('account/register.html')


@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('account/login.html')


@account_bp.route('/protected')
@jwt_required()
def protected():
    return render_template('account/protected.html')
