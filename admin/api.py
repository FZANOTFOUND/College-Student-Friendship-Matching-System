import time

from flask import render_template, redirect, url_for, request, flash
from . import api_admin_bp
from models import User
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
from sqlalchemy.orm import load_only
from constant import get_permission


@api_admin_bp.route('/query/time_period', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def statistics():
    """
    返回一段时间内有多少个用户登陆过（活跃用户）， 新增多少个用户
    :return:
    """
    try:
        start_time = request.args.get("start_time", 0)
        end_time = request.args.get("end_time", int(time.time()))
        login_users = (User.query
                       .options(load_only(User.user_id, User.username, User.age, User.gender, User.last_login_at,
                                          User.created_at))
                       .filter((User.last_login_at >= start_time) & (User.last_login_at <= end_time) &
                               User.role == "user")
                       .order_by(User.last_login_at))
        create_users = (User.query
                        .filter((User.last_login_at >= start_time) & (User.last_login_at <= end_time) &
                                (User.created_at >= start_time) & (User.created_at <= end_time) & User.role == "user")
                        .order_by(User.last_login_at))

        res = {
            "code": 200,
            "message": "Ok query finish",
            "errors": {},
            "data": {
                "user": {

                }
            }
        }
        res["data"]["total_user"] = len(login_users)
        res["data"]["new_user"] = len(login_users)
        return res, 200
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": "Inner Error :(",
            "errors": {},
            "data": {}
        }), 500
