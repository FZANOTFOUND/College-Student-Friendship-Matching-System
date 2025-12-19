from flask import Blueprint, render_template, current_app, request, abort, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from werkzeug.exceptions import HTTPException
from extensions import jwt
errors_bp = Blueprint('errors', __name__)

ERROR_MESSAGES = {
    400: ("Bad Request", "请求无效。请检查请求参数或数据格式。"),
    401: ("Unauthorized", "您未登录或身份验证失败。"),
    403: ("Forbidden", "抱歉，您没有权限访问此资源。"),
    404: ("Not Found", "您访问的页面不存在或已被移除。"),
    500: ("Internal Server Error", "服务器遇到意外情况，无法完成请求。"),
    502: ("Bad Gateway", "服务器遇到意外情况，无法完成请求。"),
}


def get_message_for_code(code: int):
    return ERROR_MESSAGES.get(code, (f"Error {code}", "发生了意外情况。"))


@errors_bp.app_errorhandler(HTTPException)
def handle_http_exception(e):
    code = e.code or 500
    title, message = get_message_for_code(code)

    # 如果 APP 在 debug 模式，显示更详细的异常字符串；否则使用 exception 自带的 description（如果有）
    if current_app.debug:
        details = str(e)
    else:
        details = getattr(e, 'description', None)

    # current_app.logger.warning("HTTPException handled: %s", e)
    return render_template('error.html', code=code, title=title, message=message, details=details), code


# 应用级的未捕获异常处理（500）
@errors_bp.app_errorhandler(Exception)
def handle_exception(e):
    code = 500
    title, message = get_message_for_code(code)

    # Debug 模式下把异常信息返回给前端（便于开发），否则不泄露细节
    details = str(e) if current_app.debug else None

    # 记录堆栈到日志（非常建议）
    current_app.logger.exception("Unhandled exception:")

    return render_template('error.html', code=code, title=title, message=message, details=details), code


@jwt.unauthorized_loader
def handle_missing_token(error_msg):
    return jsonify({
        "code": 401,
        "message": "Missing Authorization Header",
        "errors": {

        },
        "data": {

        }
    }), 401


# 场景2：Token已过期
@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return jsonify({
        "code": 401,
        "message": "Expired token loader",
        "errors": {

        },
        "data": {

        }
    }), 401


# 场景3：Token无效（篡改/格式错误）
@jwt.invalid_token_loader
def handle_invalid_token(error_msg):
    return jsonify({
        "code": 401,
        "message": "Invalid token loader",
        "errors": {

        },
        "data": {

        }
    }), 401


# 场景4：Token被吊销（可选，如登出后Token拉黑）
@jwt.revoked_token_loader
def handle_revoked_token(jwt_header, jwt_payload):
    return jsonify({
        "code": 401,
        "message": "Revoked token loader",
        "errors": {

        },
        "data": {

        }
    }), 401
