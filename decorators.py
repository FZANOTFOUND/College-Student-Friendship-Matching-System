from functools import wraps
from flask import render_template, make_response, jsonify
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt,
)
from constant import get_permission


def my_jwt_required(limit: int = 0, api: bool = False):
    """
    特殊的介于 执行函数和 路由间的装饰器
    相当于 jwt_required ，加了 401 返回 login 和 403 提示
    如果是 api 返回 json 数据
    否则返回界面
    :return:
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 1. 验证 JWT（未登录 / 过期）
            try:
                verify_jwt_in_request()
            except Exception:
                if api:
                    return jsonify({
                        "code": 401,
                        "message": "Missing Authorization Header/Token expired",
                        "errors": {

                        },
                        "data": {

                        }
                    }), 401
                else:
                    return make_response(
                        render_template("redirect_on_401.html"),
                        401
                    )

            # 2. 验证权限
            claims = get_jwt()
            role = claims.get("role", "user")
            p = get_permission(role)
            if p < limit:  # 没有达到对应的权限
                if api:
                    return jsonify({
                        "code": 403,
                        "message": "You are not allowed to view the requests page",
                        "errors": {

                        },
                        "data": {

                        }
                    }), 403
                else:
                    return render_template("error.html", code=403, details="You are not allowed to view the request "
                                                                           "page"), 403

            # 3. 放行
            return fn(*args, **kwargs)

        return wrapper

    return decorator
