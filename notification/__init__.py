from flask import Blueprint

api_notification_bp = Blueprint('api_notification', __name__, url_prefix='/api/notifications')
notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')

from . import api
from . import views
