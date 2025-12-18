import time

from flask import render_template, redirect, url_for, request, flash
from . import account_bp, api_account_bp
from models import User
from .forms import RegisterForm, LoginForm
import string
import random
import re
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_mail import Message
from datetime import datetime, timedelta
from werkzeug.datastructures import MultiDict
from werkzeug.security import generate_password_hash, check_password_hash  # 对密码进行加密
from extensions import mail, db
from models import EmailVerification, User
from decorators import *


@api_account_bp.route('/register', methods=['POST'])
def register():
    try:
        if request.is_json:
            json_data = request.get_json()
            form_data = MultiDict(json_data)
        else:
            form_data = request.form

        form = RegisterForm(form_data)
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data
            gender = form.gender.data
            age = form.age.data

            hashed_password = generate_password_hash(password)
            user = User(email=email, username=username, password_hash=hashed_password, gender=gender, age=age)
            db.session.add(user)
            db.session.commit()
            db.session.close()

            return jsonify({
                "code": 200,
                "message": "注册成功",
                "errors": {

                },
                "data": {

                }
            }), 200
        else:
            return jsonify({
                "code": 400,
                "message": "注册失败",
                "errors": form.errors,
                "data": {

                }
            }), 400
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_account_bp.route('/login', methods=['POST'])
def login():
    try:
        if request.is_json:
            json_data = request.get_json()
            form_data = MultiDict(json_data)
        else:
            form_data = request.form
        form = LoginForm(form_data)
        if form.validate():
            email = form.email.data
            password = form.password.data

            user = User.query.filter(User.email == email).first()
            if not user:
                return jsonify({
                    "code": 400,
                    "message": "登录失败",
                    "errors": {
                        "邮箱": ["邮箱不存在"]
                    },
                    "data": {

                    }
                }), 400

            if check_password_hash(user.password_hash, password):
                remember = form_data.get("remember", False)
                expires = (
                    timedelta(days=7) if remember
                    else timedelta(hours=2)
                )
                access_token = create_access_token(
                    identity=str(user.user_id),
                    expires_delta=expires
                )
                resp = jsonify({
                    "code": 200,
                    "message": "登录成功",
                    "errors": {
                    },
                    "data": {
                        "email": user.email,
                        "id": user.user_id,
                        "username": user.username,
                        "avatar_url": user.avatar_url,
                        "gender": user.gender,
                        "age": user.age,
                        "bio": user.bio,
                        "token": access_token
                    }
                })
                set_access_cookies(resp, access_token)
                return resp, 200
            else:
                return jsonify({
                    "code": 400,
                    "message": "登录失败",
                    "errors": {
                        "密码": ["密码错误"]
                    },
                    "data": {

                    }
                }), 400
        else:
            return jsonify({
                "code": 400,
                "message": "登录成功",
                "errors": form.errors,
                "data": {

                }
            }), 400
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)]
            },
            "data": {

            }
        }), 500


@api_account_bp.route('/code/email', methods=['GET'])
def get_email_captcha():
    """获取邮箱验证码"""
    email = request.args.get('email')
    EmailVerification.query.filter_by(email=email).delete()
    source = string.digits * 4
    code = random.sample(source, 4)
    code = ''.join(code)
    t = time.localtime(time.time())
    message = Message(subject='流萤快报', recipients=[email],
                      html=render_template("email.html", code=code, hour=t.tm_hour))
    mail.send(message)
    email_captcha = EmailVerification(email=email, code=code)
    db.session.add(email_captcha)
    db.session.commit()
    db.session.close()
    return jsonify({'code': 200, 'message': '发送成功'})


@api_account_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    resp = jsonify({'code': 200, 'message': '登出成功'})
    unset_jwt_cookies(resp)
    return resp


@api_account_bp.route('/profile', methods=['GET'])
@my_jwt_required(limit=0, api=True)
def get_profile():
    """获取当前用户个人资料"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'}), 404
        return jsonify({'code': 200, 'data': user.to_dict()})
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Inner Error'}), 500
