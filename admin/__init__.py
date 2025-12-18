from flask import Blueprint

api_admin_bp = Blueprint('api_admin', __name__, template_folder='../templates', static_folder='../static')

from . import api
