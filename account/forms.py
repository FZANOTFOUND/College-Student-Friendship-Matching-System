from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, IntegerField,TextAreaField
from wtforms.validators import Email, Length, EqualTo, Regexp, ValidationError, NumberRange

from models import User,EmailVerification
from extensions import db


class RegisterForm(Form):
    email = StringField(validators=[Email(message='邮箱格式错误')])
    code = StringField(validators=[Length(min=4, max=4, message='验证码长度错误')])
    username = StringField(validators=[Length(min=2, max=20, message='用户名长度错误')])
    password = StringField(validators=[Length(min=8, max=20, message='密码长度错误')])
    confirm_password = StringField(validators=[EqualTo('password', message='密码不一致')])
    gender = StringField(validators=[Regexp(r'^(男|女|其他)$', message='性别格式错误')])
    age = IntegerField(validators=[validators.NumberRange(min=18, max=100, message='年龄格式错误')])

    # 1.邮箱注册
    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValidationError('邮箱已被注册')

    # 2.验证码
    def validate_code(self, field):  # self指向当前表单对象，field为当前字段数据

        code = field.data
        email = self.email.data
        captcha_model = EmailVerification.query.filter_by(email=email, code=code).first()
        print(captcha_model)

        if not code:
            raise ValidationError('邮箱或者验证码错误')
        if captcha_model is None:
            raise ValidationError('邮箱或者验证码错误')
        if captcha_model.expire_time < datetime.now():
            raise ValidationError('验证码已过期，请重新获取')
        else:
            if captcha_model is not None:
                db.session.delete(captcha_model)
                db.session.commit()

    # 3.用户名
    def validate_username(self, field):
        username = field.data
        user = User.query.filter_by(username=username).first()
        if user:
            raise ValidationError('用户名已被使用')


class LoginForm(Form):
    email = StringField(validators=[Email(message='邮箱格式错误')])
    password = StringField(validators=[Length(min=8,max=20,message='密码长度错误')])

class EmailCaptchaRequestForm(Form):
    email = StringField('email', validators=[Email(message='邮箱格式错误')])

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            raise ValidationError('邮箱已被注册')

class ProfileEditForm(Form):
    username = StringField(validators=[Length(min=2, max=20, message='用户名长度错误')])
    gender = StringField(validators=[Regexp(r'^(男|女|其他)$', message='性别格式错误')])
    age = IntegerField(validators=[NumberRange(min=18, max=100, message='年龄格式错误')])
    bio = TextAreaField(validators=[Length(max=100, message='个人简介不能超过100字')])
    avatar_url = StringField(validators=[Length(max=255, message='头像URL过长')])
