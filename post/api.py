import time

from flask import render_template, redirect, url_for, request, flash
from . import api_post_bp
from models import User, Post
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
from models import *
from decorators import *
import traceback
from .forms import *


@api_post_bp.route('/create', methods=['PUT'])
@my_jwt_required(limit=0, api=False)
def create_post():
    try:
        if request.is_json:
            json_data = request.get_json()
            form_data = MultiDict(json_data)
        else:
            form_data = request.form

        form = PostForm(form_data)
        if form.validate():
            post = Post(user_id=get_jwt_identity(), title=form_data['title'], content=form_data['content'])
            db.session.add(post)
            db.session.commit()
            return jsonify({
                "code": 200,
                "message": "success"
            }), 200
        else:
            return jsonify({
                "code": 400,
                "message": "errors",
                "errors": form.errors
            }), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/allow/post', methods=['GET'])
@my_jwt_required(limit=1, api=False)
def allow_post():
    try:
        post_id = request.args.get('post_id')
        if not post_id:
            return jsonify({
                "code": 400,
                "message": "帖子id不能为空"
            }), 400
        reviewed_by = get_jwt_identity()
        review_notes = request.args.get('notes', "")

        post = Post.query.filter_by(id=post_id).first()
        if not post:
            return jsonify({
                "code": 404,
                "message": "帖子不存在"
            }), 404
        if post.status == "ok":
            return jsonify({
                "code": 400,
                "message": "已审核"
            }), 400
        post.status = "ok"
        post.reviewed_by = reviewed_by
        post.review_notes = review_notes
        db.session.add(post)
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "审核成功"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/like', methods=['GET'])
@my_jwt_required(limit=0, api=False)
def like_post():
    try:
        post_id = request.args.get('post_id')
        if not post_id:
            return jsonify({
                "code": 400,
                "message": "帖子id不能为空"
            }), 400
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            return jsonify({
                "code": 404,
                "message": "帖子不存在"
            }), 404
        pp = PostLike.query.filter_by(post_id=post_id, user_id=get_jwt_identity()).first()
        if pp:
            return jsonify({
                "code": 400,
                "message": "点过赞了喵"
            }), 400
        post_like = PostLike(post_id=post_id, user_id=get_jwt_identity())
        db.session.add(post_like)
        db.session.commit()
        post.likes_count += 1
        db.session.add(post)
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "点赞成功"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/comment', methods=['GET'])
@my_jwt_required(limit=0, api=False)
def comment_post():
    try:
        post_id = request.args.get('post_id')
        if not post_id:
            return jsonify({
                "code": 400,
                "message": "帖子id不能为空"
            }), 400
        content = request.args.get('content', "")
        if len(content) <= 0:
            return jsonify({
                "code": 400,
                "message": "评论过短"
            }), 400
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            return jsonify({
                "code": 404,
                "message": "帖子不存在"
            }), 404
        pp = PostComment.query.filter_by(post_id=post_id, user_id=get_jwt_identity()).first()
        if pp:
            return jsonify({
                "code": 400,
                "message": "评论过了喵"
            }), 400
        post_comment = PostComment(post_id=post_id, user_id=get_jwt_identity(), content=content)
        db.session.add(post_comment)
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "评论成功，待审核"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/allow/comment', methods=['GET'])
@my_jwt_required(limit=1, api=False)
def allow_comment():
    try:
        comment_id = request.args.get('comment_id')
        if not comment_id:
            return jsonify({
                "code": 400,
                "message": "帖子id不能为空"
            }), 400
        reviewed_by = get_jwt_identity()
        review_notes = request.args.get('notes', "")

        comment = PostComment.query.filter_by(id=comment_id).first()
        if not comment:
            return jsonify({
                "code": 404,
                "message": "帖子不存在"
            }), 404
        if comment.status == "ok":
            return jsonify({
                "code": 400,
                "message": "已审核"
            }), 400
        post = Post.query.filter(Post.id == comment.post_id).first()
        post.comments_count += 1
        db.session.add(post)
        db.session.commit()
        comment.status = "ok"
        comment.reviewed_by = reviewed_by
        comment.review_notes = review_notes
        db.session.add(comment)
        db.session.commit()
        return jsonify({
            "code": 200,
            "message": "审核成功"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/all', methods=['GET'])
@my_jwt_required(limit=0, api=False)
def all_posts():
    try:
        posts = Post.query.filter(Post.status != "pending").all()
        return jsonify({
            "code": 200,
            "message": "ok",
            "data": [
                i.to_dict(content=False) for i in posts
            ]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/single', methods=['GET'])
@my_jwt_required(limit=0, api=False)
def single_post():
    try:
        post_id = request.args.get("post_id")
        if not post_id:
            return jsonify({
                "code": 400,
                "message": "帖子id不能为空"
            }), 400
        claims = get_jwt()
        role = claims.get("role", "user")
        p = get_permission(role)
        if p < 1:
            post = Post.query.filter(Post.id == post_id, Post.status != "pending").first()
        else:

            post = Post.query.filter(Post.id == post_id).first()
        if not post:
            return jsonify({
                "code": 404,
                "message": "帖子不存在"
            }), 404
        if post.status != "pending":
            post.view_count += 1
            db.session.add(post)
            db.session.commit()
        return jsonify({
            "code": 200,
            "message": "ok",
            "data": [
                post.to_dict(content=True),
            ]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/post/pending', methods=['GET'])
@my_jwt_required(limit=1, api=False)
def pending_posts():
    try:
        posts = Post.query.filter(Post.status == "pending").all()
        return jsonify({
            "code": 200,
            "message": "ok",
            "data": [
                i.to_dict(content=True) for i in posts
            ]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/comment/pending', methods=['GET'])
@my_jwt_required(limit=1, api=False)
def pending_comments():
    try:
        comments = PostComment.query.filter(PostComment.status == "pending").all()
        return jsonify({
            "code": 200,
            "message": "ok",
            "data": [
                i.to_dict() for i in comments
            ]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500


@api_post_bp.route('/post/get_comment', methods=['GET'])
@my_jwt_required(limit=0, api=False)
def get_comments():
    try:
        post_id = request.args.get("post_id")
        if not post_id:
            return jsonify({
                "code": 400,
                "message": "帖子id不能为空"
            }), 400
        post = Post.query.filter_by(id=post_id).first()
        if not post:
            return jsonify({
                "code": 404,
                "message": "帖子不存在"
            }), 404
        comments = PostComment.query.filter_by(post_id=post_id).all()
        return jsonify({
            "code": 200,
            "message": "ok",
            "data": [
                i.to_dict() for i in comments
            ]
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器错误",
            "errors": {
                "服务器": [str(e)],
            },
            "data": {

            }
        }), 500
