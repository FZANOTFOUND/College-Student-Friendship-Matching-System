import os
from datetime import timedelta
from urllib.parse import quote_plus

# 文件上传相关配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 限制文件大小（100MB）

# 服务器设置
FLASK_RUN_HOST = '0.0.0.0'
FLASK_RUN_PORT = '8888'
FLASK_DEBUG = 1

# 数据库设置
SECRET_KEY = '534@fsdft54323'
DB_USER = "gaussdb"
DB_PASSWORD_RAW = "@Xf5133023"
DB_PASSWORD = quote_plus(DB_PASSWORD_RAW)
DB_HOST = "127.0.0.1"
DB_NAME = "postgres"
DB_PORT = 5432
SQLALCHEMY_DATABASE_URI = f'opengauss+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = '2629669459@qq.com'
MAIL_PASSWORD = 'vfgbjjhroicgdjfg'
MAIL_DEFAULT_SENDER = '2629669459@qq.com'

JWT_SECRET_KEY = "super-secret-key"

# 使用 cookie 存 JWT
JWT_TOKEN_LOCATION = ["cookies"]

# Cookie 名
JWT_ACCESS_COOKIE_NAME = "access_token"
JWT_REFRESH_COOKIE_NAME = "refresh_token"

# 防 CSRF（强烈建议）
JWT_COOKIE_CSRF_PROTECT = True,

# 跨域必须
JWT_COOKIE_SAMESITE = "Lax"
JWT_COOKIE_SECURE = False  # https 才能用（开发时可 False）

# 默认 access token 过期时间
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
