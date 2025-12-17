import os
from datetime import timedelta

# 文件上传相关配置
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 限制文件大小（100MB）

# 服务器设置
FLASK_RUN_HOST = '0.0.0.0'
FLASK_RUN_PORT = '8888'
FLASK_DEBUG = 1

# 数据库设置
SECRET_KEY = '534@fsdft54323'
SQLALCHEMY_DATABASE_URI = 'opengauss+psycopg2://gaussdb:%40Xf5133023@127.0.0.1:5432/postgres'

MAIL_SERVER = "smtp.qq.com"
MAIL_USE_SSL = True
MAIL_PORT = 465
MAIL_USERNAME = '2629669459@qq.com'
MAIL_PASSWORD = 'vfgbjjhroicgdjfg'
MAIL_DEFAULT_SENDER = '2629669459@qq.com'
