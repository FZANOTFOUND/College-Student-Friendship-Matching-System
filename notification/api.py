from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from werkzeug.datastructures import MultiDict
from models import Notification
from . import api_notification_bp
from decorators import *
from .forms import NotificationForm
import traceback

@api_notification_bp.route('/all', methods=['GET'])
@my_jwt_required(limit=0, api=True)
def get_notifications():
    """获取当前用户的通知列表"""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    notifications = Notification.query.filter_by(recipient_id=user_id) \
        .order_by(Notification.created_at.desc()) \
        .paginate(page=page, per_page=per_page)

    return jsonify({
        'code': 200,
        'data': {
            'items': [
                {
                    'notify_id': n.notify_id,
                    'type': n.type,
                    'content': n.content,
                    'related_id': n.related_id,
                    'created_at': n.created_at.isoformat(),
                    'is_read': n.is_read
                } for n in notifications.items
            ],
            'total': notifications.total,
            'page': page,
            'per_page': per_page,
            'pages': notifications.pages
        }
    })


@api_notification_bp.route('/<int:notify_id>/read', methods=['PUT'])
@my_jwt_required(limit=0, api=True)
def mark_as_read(notify_id):
    """标记通知为已读"""
    user_id = get_jwt_identity()

    notification = Notification.query.filter_by(
        notify_id=notify_id,
        recipient_id=user_id
    ).first()

    if not notification:
        return jsonify({'code': 404, 'message': '通知不存在'}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({'code': 200, 'message': '已标记为已读'})


@api_notification_bp.route('/all/read', methods=['PUT'])
@my_jwt_required(limit=0, api=True)
def mark_all_as_read():
    """标记所有通知为已读"""
    user_id = get_jwt_identity()

    Notification.query.filter_by(
        recipient_id=user_id,
        is_read=False
    ).update({'is_read': True})
    db.session.commit()

    return jsonify({'code': 200, 'message': '所有通知已标记为已读'})


@api_notification_bp.route('/unread/count', methods=['GET'])
@my_jwt_required(limit=0, api=True)
def get_unread_count():
    """获取未读通知数量"""
    user_id = get_jwt_identity()

    count = Notification.query.filter_by(
        recipient_id=user_id,
        is_read=False
    ).count()

    return jsonify({'code': 200, 'data': {'count': count}})


@api_notification_bp.route('/create', methods=['PUT'])
@my_jwt_required(limit=1, api=True)
def create_notification():
    try:
        if request.is_json:
            json_data = request.get_json()
            form_data = MultiDict(json_data)
        else:
            form_data = request.form
        form = NotificationForm(form_data)
        if form.validate():
            nt = Notification(recipient_id=form_data["recipient_id"],type=form_data["type"],content=form_data["content"],related_id=get_jwt_identity())
            db.session.add(nt)
            db.session.commit()
            return jsonify({
                "code": 200,
                "message": "ok"
            })
        else:
            return jsonify({
                "code": 400,
                "message": "格式错误",
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
