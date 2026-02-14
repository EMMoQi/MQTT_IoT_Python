# 导入必要的模块
import sys
import io
import os
import logging
from flask import Flask, render_template
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import Config


# 创建 Flask 应用实例的工厂函数
# :param config_class: 配置类，默认为 Config
# :return: Flask 应用实例
def create_app(config_class=Config):
    # 获取当前文件所在目录作为基础目录
    BASE_DIR = Path(__file__).parent

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(BASE_DIR / "web" / "templates"),  # ✅ 指定模板文件夹
        static_folder=str(BASE_DIR / "web" / "static")        # ✅ 指定静态资源文件夹
    )
    # 从配置类加载配置
    app.config.from_object(config_class)

    # 确保实例目录存在
    os.makedirs(app.instance_path, exist_ok=True)

    # 配置日志记录
    _configure_logging(app)
    # 初始化扩展
    _initialize_extensions(app)
    # 注册蓝图
    _register_blueprints(app)
    # 添加核心路由
    _add_core_routes(app)
    # 验证初始化状态
    _validate_initialization(app)

    return app

# 配置应用的日志记录
# :param app: Flask 应用实例
def _configure_logging(app):
    log_path = Path(app.instance_path) / 'logs'
    os.makedirs(log_path, exist_ok=True)

    # 文件日志处理器（支持 emoji）
    file_handler = RotatingFileHandler(
        log_path / 'app.log', maxBytes=10 * 1024 * 1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # 控制台日志处理器（不使用 emoji）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    console_handler.setLevel(logging.INFO)
    app.logger.addHandler(console_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Application logging initialized")

# 初始化应用的扩展
# :param app: Flask 应用实例
def _initialize_extensions(app):
    with app.app_context():
        # 从数据库模块导入初始化函数并初始化数据库
        from app.db.database import init_db
        init_db(app)


        # 从 MQTT 模块导入客户端类并初始化 MQTT 客户端
        from app.mqtt.client import MQTTClient
        mqtt_client = MQTTClient()
        mqtt_client.init_app(app)
        app.extensions['mqtt'] = mqtt_client

# 注册应用的蓝图
# :param app: Flask 应用实例
def _register_blueprints(app):
    # 从 API 路由模块导入蓝图并注册
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

# 添加应用的核心路由
# :param app: Flask 应用实例
def _add_core_routes(app):
    # 定义根路由，返回仪表盘页面
    @app.route('/')
    def index():
        return render_template('dashboard.html')

    # 定义健康检查路由，返回应用的健康状态
    @app.route('/health')
    def health_check():
        from app.db.models import get_all_status
        mqtt = app.extensions.get('mqtt')
        return {
            'status': 'healthy',
            'mqtt': mqtt.connection_status if mqtt else False,
            'last_message': mqtt.last_message_time.isoformat() if (mqtt and mqtt.last_message_time) else None,
            'devices': [d[0] for d in get_all_status()]
        }

# 验证应用的初始化状态
# :param app: Flask 应用实例
# :raises RuntimeError: 如果 MQTT 扩展未正确初始化
def _validate_initialization(app):
    if 'mqtt' not in app.extensions:
        raise RuntimeError('MQTT extension failed')
