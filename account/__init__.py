from flask import Blueprint

account_bp = Blueprint('account', __name__, template_folder='../templates/account', static_folder='../static')
api_account_bp = Blueprint('account_api', __name__, template_folder='../templates/api')

from . import api
from . import views


