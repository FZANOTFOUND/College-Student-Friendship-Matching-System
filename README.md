# College-Student-Friendship-Matching-System

大学生交友匹配系统，基于Flask开发，支持用户认证、个人中心、对话、发帖等功能。


## 项目简介

该系统旨在为大学生提供交友匹配服务，通过用户信息分析实现相似用户推荐。


## 功能特点

- **用户认证**：支持注册、登录、登出，基于邮箱验证码验证验证
- **个人中心**：展示用户基本信息
- **交友匹配**：基于用户信息计算相似度并推荐好友


## 技术栈

- **后端**：Python + Flask + SQLAlchemy（ORM）
- **数据库**：OpenGauss
- **前端**：HTML + CSS + JavaScript + Bootstrap 5
- **认证**：JWT（JSON Web Token）
- **其他**：Flask-Mail（邮件服务）、Flask-CORS（跨域支持）


## 安装与运行

### 前提条件

- Python 3.8+
- OpenGauss数据库
- 虚拟环境工具（如venv）


### 步骤

1. **克隆仓库**
   ```bash
   git clone <仓库地址>
   cd College-Student-Friendship-Matching-System
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt 
   ```

4. **配置环境**
   - 修改`config.py`中的数据库连接、邮件服务等配置
   - 确保`.env`文件（如使用）包含必要环境变量

5. **初始化数据库**
   删除 migrate 文件夹（推荐）。
   命令行中执行以下命令
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **运行项目**
   ```bash
   python app.py
   ```
   访问 `http://localhost:8888` 即可打开系统


## 目录结构

```
College-Student-Friendship-Matching-System/
├── app.py               # 应用入口
├── config.py            # 配置文件
├── models.py            # 数据模型（用户、匹配记录等）
├── decorators.py        # 装饰器（权限管理）
├── account/             # 用户相关蓝图
│   ├── api.py           # 认证相关API
│   └── views.py         # 页面视图
├── admin/               # 管理员相关蓝图
├── posts/               # 帖子相关蓝图
├── notification/        # 通知相关蓝图
├── conversation/        # 对话相关蓝图
├── errors/              # 403/404等错误蓝图
├── templates/           # HTML模板
│   ├── base.html        # 基础模板
│   ├── index.html       # 首页
│   ├── account/         # 用户相关页面
│   └── ...     
├── static/              # 静态文件
│   ├── js/              # JavaScript脚本
│   └── css/             # 样式表
└── migrations/          # 数据库迁移文件
```


## 注意事项

- 开发环境下`FLASK_DEBUG`已开启，生产环境需关闭
- 邮件服务配置需替换为实际可用的SMTP信息
- 数据库连接字符串需根据实际部署环境修改