from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from decorators import my_jwt_required
from extensions import db
from models import Conversation, ConversationParticipant, Message, User, Notification
from datetime import datetime

api_conversation_bp = Blueprint('api_conversation', __name__, url_prefix='/api/conversations')


@api_conversation_bp.route('', methods=['GET'])
@jwt_required()
def get_conversations():
    """获取当前用户的所有对话"""
    user_id = get_jwt_identity()

    # 查询用户参与的所有对话
    participants = ConversationParticipant.query.filter_by(user_id=user_id).all()
    conv_ids = [p.conv_id for p in participants]

    conversations = []
    for conv_id in conv_ids:
        conv = Conversation.query.get(conv_id)
        if not conv or not conv.is_active:
            continue

        # 获取对话中的其他参与者
        other_participants = ConversationParticipant.query.filter(
            ConversationParticipant.conv_id == conv_id,
            ConversationParticipant.user_id != user_id
        ).all()

        # 获取最后一条消息
        last_msg = Message.query.filter_by(conv_id=conv_id).order_by(Message.sent_at.desc()).first()

        conversations.append({
            'conv_id': conv.conv_id,
            'participants': [
                {
                    'user_id': p.user_id,
                    'username': User.query.get(p.user_id).username
                } for p in other_participants
            ],
            'last_message': last_msg.content if last_msg else None,
            'updated_at': conv.updated_at.isoformat(),
            'unread_count': Message.query.filter(
                Message.conv_id == conv_id,
                Message.sender_id != user_id,
                Message.is_read == False
            ).count()
        })

    # 按更新时间排序
    conversations.sort(key=lambda x: x['updated_at'], reverse=True)
    return jsonify({'code': 200, 'data': conversations})


@api_conversation_bp.route('/<int:conv_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conv_id):
    """获取指定对话的消息列表"""
    user_id = get_jwt_identity()

    # 验证用户是否参与该对话
    participant = ConversationParticipant.query.filter_by(
        conv_id=conv_id,
        user_id=user_id
    ).first()

    if not participant:
        return jsonify({'code': 403, 'message': '无权访问此对话'}), 403

    # 获取消息
    messages = Message.query.filter_by(conv_id=conv_id).order_by(Message.sent_at).all()

    # 标记未读消息为已读
    unread_msgs = [msg for msg in messages if not msg.is_read and msg.sender_id != user_id]
    for msg in unread_msgs:
        msg.is_read = True
    db.session.commit()

    # 更新最后阅读时间
    participant.last_read_at = datetime.now()
    db.session.commit()

    return jsonify({
        'code': 200,
        'data': [
            {
                'msg_id': msg.msg_id,
                'sender_id': msg.sender_id,
                'sender_name': User.query.get(msg.sender_id).username,
                'content': msg.content,
                'sent_at': msg.sent_at.isoformat(),
                'is_read': msg.is_read
            } for msg in messages
        ]
    })


@api_conversation_bp.route('/<int:conv_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conv_id):
    """发送消息到指定对话"""
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({'code': 400, 'message': '消息内容不能为空'}), 400

    # 验证用户是否参与该对话
    participant = ConversationParticipant.query.filter_by(
        conv_id=conv_id,
        user_id=user_id
    ).first()

    if not participant:
        return jsonify({'code': 403, 'message': '无权访问此对话'}), 403

    # 创建消息
    message = Message(
        conv_id=conv_id,
        sender_id=user_id,
        content=data['content']
    )
    db.session.add(message)

    # 更新对话时间
    conv = Conversation.query.get(conv_id)
    conv.updated_at = datetime.now()

    db.session.commit()

    # 创建通知给其他参与者
    other_participants = ConversationParticipant.query.filter(
        ConversationParticipant.conv_id == conv_id,
        ConversationParticipant.user_id != user_id
    ).all()

    for p in other_participants:
        notification = Notification(
            recipient_id=p.user_id,
            type='message',
            content=f'收到来自 {User.query.get(user_id).username} 的消息',
            related_id=conv_id
        )
        db.session.add(notification)

    db.session.commit()

    return jsonify({
        'code': 201,
        'data': {
            'msg_id': message.msg_id,
            'sent_at': message.sent_at.isoformat()
        }
    })


@api_conversation_bp.route('/new', methods=['POST'])
@my_jwt_required(api=True)
def create_conversation():
    """创建新对话"""

    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or not data.get('recipient_id'):
        return jsonify({'code': 400, 'message': '请指定对话对象'}), 400

    recipient_id = data['recipient_id']

    # 检查用户是否存在
    if not User.query.get(recipient_id):
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    # 检查是否已有对话
    existing_conv = db.session.query(ConversationParticipant.conv_id).filter(
        ConversationParticipant.user_id == user_id
    ).intersect(
        db.session.query(ConversationParticipant.conv_id).filter(
            ConversationParticipant.user_id == recipient_id
        )
    ).first()

    if existing_conv:
        return jsonify({
            'code': 200,
            'data': {'conv_id': existing_conv[0]}
        })

    # 创建新对话
    conv = Conversation()
    db.session.add(conv)
    db.session.commit()

    # 添加参与者
    participant1 = ConversationParticipant(conv_id=conv.conv_id, user_id=user_id)
    participant2 = ConversationParticipant(conv_id=conv.conv_id, user_id=recipient_id)
    db.session.add_all([participant1, participant2])
    db.session.commit()

    return jsonify({
        'code': 201,
        'data': {'conv_id': conv.conv_id}
    })
