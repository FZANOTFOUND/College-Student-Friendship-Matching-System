from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email
import wtforms
from wtforms.validators import Email, Length, EqualTo, Regexp
from models import User,EmailVerification
from extensions import db


class RegisterForm(wtforms.Form):
    email = wtforms.StringField(validators=[Email(message='邮箱格式错误')])
    code = wtforms.StringField(validators=[Length(min=4, max=4, message='验证码长度错误')])
    username = wtforms.StringField(validators=[Length(min=2, max=20, message='用户名长度错误')])
    password = wtforms.StringField(validators=[Length(min=8, max=20, message='密码长度错误')])
    confirm_password = wtforms.StringField(validators=[EqualTo('password', message='密码不一致')])
    gender = wtforms.StringField(validators=[Regexp(r'^(男|女|其他)$', message='性别格式错误')])
    age = wtforms.IntegerField(validators=[wtforms.validators.NumberRange(min=18, max=100, message='年龄格式错误')])

    def validate_code(self, field):  # self指向当前表单对象，field为当前字段数据
        code = field.data
        email = self.email.data
        captcha_model = EmailVerification.query.filter_by(email=email, code=code).first()
        if not code:
            raise wtforms.ValidationError('邮箱或者验证码错误')
        else:
            if captcha_model is not None:
                db.session.delete(captcha_model)
                db.session.commit()


class LoginForm(FlaskForm):
    email = wtforms.StringField(validators=[Email(message='邮箱格式错误')])
    password = wtforms.StringField(validators=[Length(min=8,max=20,message='密码长度错误')])