from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import Form, StringField, validators, IntegerField,TextAreaField
from wtforms.validators import Email, Length, EqualTo, Regexp, ValidationError, NumberRange, DataRequired

from models import User,EmailVerification
from extensions import db


class NotificationForm(Form):
    recipient_id = StringField('Recipient', validators=[DataRequired(message="收信人不能为空")])
    type = StringField('Type', validators=[DataRequired(message="类型不能为空")])
    content = TextAreaField('Content', validators=[DataRequired(message="内容不能为空")])