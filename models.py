from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timedelta
from extensions import db, bcrypt


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None
        }


# 邮箱验证码表
class EmailVerification(db.Model):
    __tablename__ = 'email_verification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(4), nullable=False)
    expire_time = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(minutes=10))


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

