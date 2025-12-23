from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, IntegerField,TextAreaField
from wtforms.validators import Email, Length, EqualTo, Regexp, ValidationError, NumberRange

from models import User,EmailVerification
from extensions import db


class PostForm(Form):
    title = StringField('Title', validators=[validators.DataRequired(message="标题不能为空")])
    content = TextAreaField('Content', validators=[Length(min=5, message='帖子过短')])

