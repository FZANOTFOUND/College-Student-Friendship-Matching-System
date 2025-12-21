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
from sqlalchemy import func
from datetime import datetime, timezone
import traceback


def parse_datetime(param, default):
    if not param:
        return default
    try:
        # 兼容 Z 结尾
        return datetime.fromisoformat(param.replace('Z', '+00:00'))
    except ValueError:
        return default


def to_utc_z(dt):
    if not dt:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


@api_admin_bp.route('/query/time_period', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def statistics():
    """
    返回一段时间内有多少个用户登陆过（活跃用户）， 新增多少个用户
    :return:
    """
    try:
        default_start = datetime(1, 1, 1, tzinfo=timezone.utc)
        default_end = datetime.now()

        # 解析参数
        s = parse_datetime(request.args.get('start_time'), default_start)
        e = parse_datetime(request.args.get('end_time'), default_end)

        # 新建用户
        new_users = (
            User.query
            .filter(User.created_at >= s, User.created_at <= e)
            .all()
        )

        # 登录过的用户
        login_users = (
            User.query
            .filter(
                User.last_login_at.isnot(None),
                User.last_login_at >= s,
                User.last_login_at <= e
            )
            .all()
        )

        return jsonify({
            "code": 200,
            "start_time": to_utc_z(s),
            "end_time": to_utc_z(e),
            "new_users": [
                {
                    "user_id": u.user_id,
                    "username": u.username
                } for u in new_users
            ],
            "login_users": [
                {
                    "user_id": u.user_id,
                    "username": u.username
                } for u in login_users
            ]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "Inner Error :(",
            "errors": {},
            "data": {}
        }), 500


@api_admin_bp.route('/me', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def me():
    return jsonify({
        "code": 200,
        "message": "ok",
    }), 200
