from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from extensions import db, bcrypt
from sqlalchemy import func, Index, Text, text, DDL, event, and_, desc

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.now())
    last_login_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    role = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'age': self.age,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            "role": self.role,
        }


# 邮箱验证码表
class EmailVerification(db.Model):
    __tablename__ = 'email_verification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(4), nullable=False)
    expire_time = db.Column(db.DateTime, default=datetime.now())


# 在现有models.py中添加匹配记录模型
class MatchRecord(db.Model):
    __tablename__ = 'match_records'

    match_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    similarity_score = db.Column(db.Numeric(5, 4))
    matched_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # 关联用户
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='matches_as_user1')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='matches_as_user2')


class Tag(db.Model):
    __tablename__ = "tags"

    tag_id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(50), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # # 关系（可选）
    # users = db.relationship(
    #     "User",
    #     secondary="user_tags",
    #     back_populates="tags"
    # )

    def __repr__(self):
        return f"<Tag(id={self.tag_id}, name={self.tag_name})>"

    def to_dict(self):
        return {
            "tag_id": self.tag_id,
            "tag_name": self.tag_name,
            "category": self.category,
            "description": self.description,
            "created_at": self.created_at
        }


class UserTag(db.Model):
    __tablename__ = "user_tags"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    tag_id = db.Column(
        db.Integer,
        db.ForeignKey("tags.tag_id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at = db.Column(db.DateTime, default=datetime.now)

    #
    # # 关系（可选）
    # user = db.relationship("User", back_populates="user_tags")
    # tag = db.relationship("Tag")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "tag_id": self.tag_id,
            "created_at": self.created_at
        }

class Conversation(db.Model):
    __tablename__ = 'conversations'

    conv_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = db.Column(db.Boolean, default=True)

    # 关联消息
    messages = db.relationship('Message', backref='conversation', lazy=True, cascade="all, delete-orphan")


class ConversationParticipant(db.Model):
    __tablename__ = 'conversation_participants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conv_id = db.Column(db.Integer, db.ForeignKey('conversations.conv_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.now)
    last_read_at = db.Column(db.DateTime)

    # 联合唯一约束
    __table_args__ = (db.UniqueConstraint('conv_id', 'user_id', name='unique_conv_user'),)


class Message(db.Model):
    __tablename__ = 'messages'

    msg_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conv_id = db.Column(db.Integer, db.ForeignKey('conversations.conv_id', ondelete='CASCADE'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now)
    is_read = db.Column(db.Boolean, default=False)

    # 关联发送者
    sender = db.relationship('User', backref='sent_messages')


class Notification(db.Model):
    __tablename__ = 'notifications'

    notify_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'message', 'match', etc.
    content = db.Column(db.Text, nullable=False)
    related_id = db.Column(db.Integer)  # 关联的资源ID（如对话ID）
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_read = db.Column(db.Boolean, default=False)

    # 关联接收者
    recipient = db.relationship('User', backref='notifications')


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    review_notes = db.Column(Text)
    reviewed_at = db.Column(db.DateTime, onupdate=datetime.now)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def to_dict(self, content=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'status': self.status,
            'likes_count': self.likes_count,
            'comments_count': self.comments_count,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if content:
            data['content'] = self.content
        return data


class PostLike(db.Model):
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_post_like'),
    )


class PostComment(db.Model):
    __tablename__ = 'post_comments'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comments.id', ondelete='CASCADE'), index=True)
    content = db.Column(Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    review_notes = db.Column(Text)
    reviewed_at = db.Column(db.DateTime, onupdate=datetime.now)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def to_dict(self):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'content': self.content,
        }
        return data
