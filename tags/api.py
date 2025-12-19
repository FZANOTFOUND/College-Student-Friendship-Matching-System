import time
import json
from flask import render_template, redirect, url_for, request, flash
from models import Tag, UserTag
from . import api_tags_bp
import string
import random
import re
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies
)
from collections import defaultdict
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_mail import Message
from datetime import datetime, timedelta
from werkzeug.datastructures import MultiDict
from werkzeug.security import generate_password_hash, check_password_hash  # 对密码进行加密
from extensions import mail, db
from models import EmailVerification, User
from decorators import *
from sqlalchemy.exc import IntegrityError


@api_tags_bp.route('/all', methods=['GET'])
@my_jwt_required(limit=0, api=True)
def get_all_tags():
    try:
        res = Tag.query.all()

        grouped = {}
        for t in res:
            grouped.setdefault(t.category, []).append({
                "tag_id": t.tag_id,
                "tag_name": t.tag_name,
                "description": t.description
            })
        return jsonify({"code": 200,
                        "message": "success",
                        'data': grouped}), 200
    except Exception as e:
        # print(e)
        return jsonify({"code": 500,
                        "message": "Inner Error :(",
                        "errors": {

                        }}), 500


@api_tags_bp.route('/user', methods=['GET'])
@my_jwt_required(limit=0, api=True)
def get_user_tags():
    try:
        user_id = get_jwt_identity()
        res = UserTag.query.filter_by(user_id=user_id).all()
        tag_ids = [r.tag_id for r in res]
        return jsonify({"code": 200,
                        "message": "success",
                        'data': tag_ids}), 200
    except Exception as e:
        print(e)
        return jsonify({"code": 500,
                        "message": "Inner Error :(",
                        "errors": {

                        }}), 500


@api_tags_bp.route('/change', methods=['PUT', 'DELETE'])
@my_jwt_required(limit=0, api=True)
def change_tag():
    try:
        data = request.get_json() or {}
        tag_id = data.get("tag_id")
        if tag_id is None:
            return jsonify({
                "code": 400, "error": "missing tag_id"}), 400
        user_id = get_jwt_identity()
        if request.method == "PUT":
            # 添加关系（幂等）
            exists = UserTag.query.filter_by(user_id=user_id, tag_id=tag_id).first()
            if exists:
                return jsonify({"code": 200, "message": "already exists"}), 200
            try:
                ut = UserTag(user_id=user_id, tag_id=tag_id)
                db.session.add(ut)
                db.session.commit()
                return jsonify({"code": 201, "message": "added"}), 201
            except IntegrityError:
                db.session.rollback()
                return jsonify({"code": 500, "error": "invalid tag_id or constraint error"}), 500

        else:  # DELETE
            ut = UserTag.query.filter_by(user_id=user_id, tag_id=tag_id).first()
            if not ut:
                return jsonify({"code": 200, "message": "not found"}), 200
            db.session.delete(ut)
            db.session.commit()
            return jsonify({"code": 200, "message": "deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 500, "error": "Inner Error"}), 500

def jaccard_similarity(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)

@api_tags_bp.route("/recommend", methods=["GET"])
@my_jwt_required(limit=0, api=True)
def recommend_users():
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"code": 400, "error": "missing user_id"}), 400
        # 1. 当前用户的 tag 集合
        my_tags = {
            ut.tag_id
            for ut in UserTag.query.filter_by(user_id=current_user_id).all()
        }
        # 2. 读取所有用户的 tag
        user_tags_map = defaultdict(set)
        all_user_tags = UserTag.query.all()
        for u in User.query.all():
            user_tags_map[u.user_id]
        for ut in all_user_tags:
            user_tags_map[ut.user_id].add(ut.tag_id)


        # 3. 计算相似度
        scores = []
        for user_id, tags in user_tags_map.items():
            if user_id == current_user_id:
                continue

            score = jaccard_similarity(my_tags, tags)
            scores.append((user_id, score))

        # 4. 排序 & 取前 10
        scores.sort(key=lambda x: x[1], reverse=True)
        top_users = scores[:10]

        # 5. 查询用户信息
        users = (
            User.query
            .filter(User.user_id.in_([u[0] for u in top_users]))
            .all()
        )

        user_info = {u.user_id: u for u in users}

        result = []
        for user_id, score in top_users:
            user = user_info[user_id]
            result.append({
                "user_id": user.user_id,
                "username": user.username,
                "similarity": round(score, 3)
            })

        return jsonify(code=200, data=result)
    except Exception as e:
        return jsonify({"code": 500, "error": "Inner Error"}), 500