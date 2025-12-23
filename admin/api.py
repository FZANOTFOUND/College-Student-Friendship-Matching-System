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
from decorators import *
from sqlalchemy.orm import load_only
from constant import get_permission
from sqlalchemy import func
from datetime import datetime, timezone
import traceback
from sqlalchemy import or_, and_, desc
from models import *


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


@api_admin_bp.route('/query/users', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def get_user_list():
    """5.2 获取用户列表（管理员）"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', '')  # active, suspended
        role = request.args.get('role', '', type=str)

        # 构建查询
        query = User.query

        # 搜索条件
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.username.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )

        # 状态过滤
        if status in ['active', 'suspended']:
            query = query.filter(User.status == status)

        # 角色过滤
        if role:
            try:
                role_int = int(role)
                query = query.filter(User.role == role_int)
            except ValueError:
                pass

        # 分页查询
        pagination = query.order_by(desc(User.created_at)) \
            .paginate(page=page, per_page=per_page, error_out=False)

        users = pagination.items

        return jsonify({
            "code": 200,
            "data": {
                "items": [user.to_dict() for user in users],
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器内部错误",
            "errors": {"server": [str(e)]}
        }), 500


@api_admin_bp.route('/query/users/<int:user_id>', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def get_user_detail(user_id):
    """获取用户详细信息（管理员）"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "code": 404,
                "message": "用户不存在"
            }), 404

        # 获取用户的匹配记录
        match_records = MatchRecord.query.filter(
            or_(
                MatchRecord.user1_id == user_id,
                MatchRecord.user2_id == user_id
            )
        ).all()

        # 获取用户的标签
        user_tags = db.session.query(Tag).join(
            UserTag, Tag.tag_id == UserTag.tag_id
        ).filter(
            UserTag.user_id == user_id
        ).all()

        user_data = user.to_dict()
        user_data['match_count'] = len(match_records)
        user_data['tags'] = [tag.to_dict() for tag in user_tags]
        user_data['last_login'] = user.last_login_at.isoformat() if user.last_login_at else None

        return jsonify({
            "code": 200,
            "data": user_data
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器内部错误"
        }), 500


@api_admin_bp.route('/set/users/<int:user_id>/role', methods=['PUT'])
@my_jwt_required(limit=1, api=True)
def update_user_role(user_id):
    """更新用户角色（管理员权限）"""
    try:
        data = request.get_json()
        if not data or 'role' not in data:
            return jsonify({
                "code": 400,
                "message": "缺少角色参数"
            }), 400

        new_role = data['role']
        if not isinstance(new_role, int):
            try:
                new_role = int(new_role)
            except ValueError:
                return jsonify({
                    "code": 400,
                    "message": "角色必须是整数"
                }), 400

        # 检查当前用户是否有权限修改（超级管理员才能修改角色）
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        if current_user.role < 2:  # 假设2是超级管理员
            return jsonify({
                "code": 403,
                "message": "权限不足"
            }), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "code": 404,
                "message": "用户不存在"
            }), 404

        old_role = user.role
        user.role = new_role
        user.updated_at = datetime.now()
        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"用户角色已更新：{old_role} -> {new_role}",
            "data": user.to_dict()
        })
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "服务器内部错误"
        }), 500


@api_admin_bp.route('/conversations', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def get_conversations_monitor():
    """7.1 获取对话列表（监控）"""
    try:
        # 获取查询参数
        user_id = request.args.get('user_id', type=int)
        has_sensitive = request.args.get('has_sensitive', type=str)  # 'true' or 'false'
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 构建查询
        query = Conversation.query.filter(Conversation.is_active == True)

        # 按用户筛选
        if user_id:
            # 查找用户参与的所有对话
            conv_ids = db.session.query(ConversationParticipant.conv_id).filter(
                ConversationParticipant.user_id == user_id
            ).subquery()
            query = query.filter(Conversation.conv_id.in_(conv_ids))

        # 时间范围筛选
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Conversation.created_at >= start_dt)
            except ValueError:
                pass

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Conversation.created_at <= end_dt)
            except ValueError:
                pass

        # 敏感内容筛选（这里简化处理，实际可能需要内容分析）
        # 暂时留空，后续可以集成敏感词检测

        # 分页查询
        pagination = query.order_by(desc(Conversation.updated_at)) \
            .paginate(page=page, per_page=per_page, error_out=False)

        conversations = pagination.items

        # 获取详细数据
        conv_data = []
        for conv in conversations:
            # 获取参与者
            participants = ConversationParticipant.query.filter_by(
                conv_id=conv.conv_id
            ).all()

            # 获取最后一条消息
            last_msg = Message.query.filter_by(
                conv_id=conv.conv_id
            ).order_by(desc(Message.sent_at)).first()

            # 获取消息数量
            msg_count = Message.query.filter_by(
                conv_id=conv.conv_id
            ).count()

            # 检查是否有敏感内容（示例逻辑）
            sensitive_detected = False
            if last_msg:
                # 这里可以添加敏感词检测逻辑
                sensitive_keywords = ['违规词1', '违规词2', '广告']
                content = last_msg.content.lower()
                sensitive_detected = any(keyword in content for keyword in sensitive_keywords)

            conv_data.append({
                'conv_id': conv.conv_id,
                'participants': [
                    {
                        'user_id': p.user_id,
                        'username': User.query.get(p.user_id).username
                    } for p in participants
                ],
                'participant_count': len(participants),
                'message_count': msg_count,
                'last_message': last_msg.content[:100] + '...' if last_msg and len(
                    last_msg.content) > 100 else last_msg.content if last_msg else None,
                'last_message_time': last_msg.sent_at.isoformat() if last_msg else None,
                'sensitive_detected': sensitive_detected,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            })

        return jsonify({
            "code": 200,
            "data": {
                "items": conv_data,
                "total": pagination.total,
                "page": page,
                "per_page": per_page,
                "pages": pagination.pages
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器内部错误",
            "errors": {"server": [str(e)]}
        }), 500


@api_admin_bp.route('/conversations/<int:conv_id>', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def get_conversation_detail(conv_id):
    """获取对话详情（管理员监控）"""
    try:
        # 获取对话
        conv = Conversation.query.get(conv_id)
        if not conv:
            return jsonify({
                "code": 404,
                "message": "对话不存在"
            }), 404

        # 获取参与者
        participants = ConversationParticipant.query.filter_by(
            conv_id=conv_id
        ).all()

        # 获取消息（限制最新100条）
        messages = Message.query.filter_by(
            conv_id=conv_id
        ).order_by(desc(Message.sent_at)).limit(100).all()

        # 统计信息
        total_messages = Message.query.filter_by(conv_id=conv_id).count()

        # 检测敏感内容
        sensitive_messages = []
        sensitive_keywords = ['违规词1', '违规词2', '广告', '联系方式', '微信号']

        for msg in messages:
            content_lower = msg.content.lower()
            found_keywords = []
            for keyword in sensitive_keywords:
                if keyword in content_lower:
                    found_keywords.append(keyword)

            if found_keywords:
                sensitive_messages.append({
                    'msg_id': msg.msg_id,
                    'sender_id': msg.sender_id,
                    'sender_name': User.query.get(msg.sender_id).username,
                    'content': msg.content,
                    'sent_at': msg.sent_at.isoformat(),
                    'keywords': found_keywords
                })

        return jsonify({
            "code": 200,
            "data": {
                'conv_id': conv.conv_id,
                'participants': [
                    {
                        'user_id': p.user_id,
                        'username': User.query.get(p.user_id).username,
                        'joined_at': p.joined_at.isoformat(),
                        'last_read': p.last_read_at.isoformat() if p.last_read_at else None
                    } for p in participants
                ],
                'total_messages': total_messages,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'recent_messages': [
                    {
                        'msg_id': msg.msg_id,
                        'sender_id': msg.sender_id,
                        'sender_name': User.query.get(msg.sender_id).username,
                        'content': msg.content,
                        'sent_at': msg.sent_at.isoformat(),
                        'is_read': msg.is_read
                    } for msg in messages
                ],
                'sensitive_analysis': {
                    'total_checked': len(messages),
                    'sensitive_count': len(sensitive_messages),
                    'sensitive_messages': sensitive_messages,
                    'detection_keywords': sensitive_keywords
                }
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器内部错误"
        }), 500


@api_admin_bp.route('/conversations/<int:conv_id>/flag', methods=['POST'])
@my_jwt_required(limit=1, api=True)
def flag_conversation(conv_id):
    """7.2 标记敏感对话"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "code": 400,
                "message": "缺少请求数据"
            }), 400

        flag_type = data.get('type', 'suspicious')  # suspicious, inappropriate, spam
        reason = data.get('reason', '')
        action = data.get('action', 'warn')  # warn, mute, ban

        # 查找对话
        conv = Conversation.query.get(conv_id)
        if not conv:
            return jsonify({
                "code": 404,
                "message": "对话不存在"
            }), 404

        # 获取参与者
        participants = ConversationParticipant.query.filter_by(
            conv_id=conv_id
        ).all()

        # 这里可以记录到数据库的违规记录表中
        # 示例：创建违规记录
        # from models import ViolationRecord  # 需要先创建这个模型
        # violation = ViolationRecord(
        #     conv_id=conv_id,
        #     flag_type=flag_type,
        #     reason=reason,
        #     reported_by=get_jwt_identity(),
        # reported_at=datetime.now()
        # )
        # db.session.add(violation)

        # 根据action采取不同措施=
        if action == 'mute':
            # 临时禁言参与者
            for p in participants:
                # 这里可以添加禁言逻辑
                pass
            action_message = "参与者已被临时禁言"
        elif action == 'ban':
            # 封禁参与者
            for p in participants:
                user = User.query.get(p.user_id)
                if user:
                    user.status = 'suspended'
            action_message = "参与者已被封禁"
        else:
            action_message = "已记录警告"

        # 发送通知给参与者
        from models import Notification
        for p in participants:
            notification = Notification(
                recipient_id=p.user_id,
                type='system',
                content=f'您的对话因{reason}被管理员标记，请注意遵守社区规则',
                related_id=conv_id
            )
            db.session.add(notification)

        db.session.commit()

        return jsonify({
            "code": 200,
            "message": f"对话已标记为{flag_type}，{action_message}",
            "data": {
                'conv_id': conv_id,
                'flag_type': flag_type,
                'action_taken': action,
                'affected_users': [p.user_id for p in participants]
            }
        })
    except Exception as e:
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            "code": 500,
            "message": "服务器内部错误"
        }), 500


@api_admin_bp.route('/conversations/search', methods=['GET'])
@my_jwt_required(limit=1, api=True)
def search_conversations():
    """搜索对话内容"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword or len(keyword) < 2:
            return jsonify({
                "code": 400,
                "message": "搜索关键词至少2个字符"
            }), 400

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 搜索包含关键词的消息
        messages = Message.query.filter(
            Message.content.ilike(f'%{keyword}%')
        ).order_by(desc(Message.sent_at)) \
            .paginate(page=page, per_page=per_page, error_out=False)

        # 整理结果
        results = []
        for msg in messages.items:
            conv = Conversation.query.get(msg.conv_id)
            if not conv:
                continue

            # 获取参与者
            participants = ConversationParticipant.query.filter_by(
                conv_id=msg.conv_id
            ).all()

            # 高亮显示关键词
            content = msg.content
            highlighted = content.replace(
                keyword,
                f'<span style="background-color: yellow;">{keyword}</span>'
            )

            results.append({
                'conv_id': msg.conv_id,
                'msg_id': msg.msg_id,
                'sender_id': msg.sender_id,
                'sender_name': User.query.get(msg.sender_id).username,
                'content': content,
                'highlighted_content': highlighted,
                'sent_at': msg.sent_at.isoformat(),
                'participants': [
                    {
                        'user_id': p.user_id,
                        'username': User.query.get(p.user_id).username
                    } for p in participants
                ]
            })

        return jsonify({
            "code": 200,
            "data": {
                "keyword": keyword,
                "items": results,
                "total": messages.total,
                "page": page,
                "per_page": per_page,
                "pages": messages.pages
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": "服务器内部错误"
        }), 500