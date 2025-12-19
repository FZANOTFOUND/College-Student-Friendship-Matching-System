import config
import models
from account import account_bp, api_account_bp
from errors import errors_bp
from flask import Flask, render_template
from dotenv import load_dotenv
from flask_login import current_user
from extensions import db, mail, jwt, bcrypt, cors
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import timedelta
from admin import api_admin_bp
from tags import api_tags_bp, tags_bp
from models import *

# load env
load_dotenv()

# create app

app = Flask(__name__)

app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

# register extensions after config
db.init_app(app)
mail.init_app(app)
jwt.init_app(app)
cors._options = {"supports_credentials": True,
                 "origins": [
                     r"http://localhost:\d+",
                     r"http://127\.0\.0\.1:\d+",
                     r"http://192\.168\.\d+\.\d+:\d+",
                     r"http://10\.\d+\.\d+\.\d+:\d+",
                 ]}
cors.init_app(app)
bcrypt.init_app(app)
Migrate(app, db)

# 注册蓝图
app.register_blueprint(account_bp, url_prefix='/account')
app.register_blueprint(api_account_bp, url_prefix='/api/account')
app.register_blueprint(errors_bp)
app.register_blueprint(api_admin_bp, url_prefix='/api/admin')
app.register_blueprint(api_tags_bp, url_prefix='/api/tags')
app.register_blueprint(tags_bp, url_prefix='/tags')


@app.route('/')
def index():
    return render_template('index.html')


# CLI helper to create tables quickly
@app.cli.command('init-db')
def init_db():
    """Quick create tables (for development). In production use migrations."""
    with app.app_context():
        db.create_all()
        print("DB initialized (db.create_all()).")


def init_tags(db):
    tags = [
        # ========= 兴趣 interest =========
        ("编程", "interest", "对编程和软件开发感兴趣"),
        ("游戏", "interest", "喜欢电子游戏"),
        ("音乐", "interest", "喜欢听音乐或创作音乐"),
        ("电影", "interest", "喜欢看电影"),
        ("阅读", "interest", "有阅读习惯"),
        ("摄影", "interest", "喜欢摄影和拍照"),
        ("写作", "interest", "喜欢写文章或创作内容"),
        ("运动", "interest", "热爱体育运动"),
        ("旅行", "interest", "喜欢旅行和探索不同文化"),
        ("科技资讯", "interest", "关注科技新闻和趋势"),

        # ========= 技术 tech =========
        ("后端开发", "tech", "从事或学习后端开发"),
        ("前端开发", "tech", "从事或学习前端开发"),
        ("全栈开发", "tech", "同时关注前端与后端技术"),
        ("人工智能", "tech", "对 AI / ML / DL 感兴趣"),
        ("数据分析", "tech", "从事或学习数据分析"),
        ("大数据", "tech", "处理和分析大规模数据"),
        ("算法竞赛", "tech", "参加算法或编程竞赛"),
        ("系统设计", "tech", "关注系统架构和设计"),
        ("数据库", "tech", "关系型或非关系型数据库技术"),
        ("云计算", "tech", "云平台与分布式计算"),
        ("DevOps", "tech", "持续集成、部署与运维"),
        ("网络安全", "tech", "关注信息安全与防护"),

        # ========= 目的 purpose =========
        ("学习", "purpose", "以学习为主要目的"),
        ("工作", "purpose", "工作相关使用"),
        ("项目实践", "purpose", "做实际项目"),
        ("求职准备", "purpose", "为找工作或面试做准备"),
        ("技能提升", "purpose", "系统性提升技术能力"),
        ("兴趣探索", "purpose", "出于兴趣进行探索"),

        # ========= 用户特征 profile =========
        ("学生", "profile", "在校学生"),
        ("在职", "profile", "已经工作"),
        ("开发者", "profile", "软件开发人员"),
        ("转行中", "profile", "正在进行职业转型"),
        ("自由职业", "profile", "自由职业者"),
        ("应届生", "profile", "即将或刚毕业"),
        ("技术管理", "profile", "技术负责人或管理角色"),
    ]

    for name, category, desc in tags:
        if not Tag.query.filter_by(tag_name=name).first():
            db.session.add(Tag(
                tag_name=name,
                category=category,
                description=desc
            ))
    db.session.commit()

# @app.route('/init-db')
# def init_db():
#     init_tags(db)

if __name__ == '__main__':
    app.run(host=config.FLASK_RUN_HOST, port=config.FLASK_RUN_PORT, debug=config.FLASK_DEBUG)
