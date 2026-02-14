# 导入应用工厂函数
from app import create_app
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'


# 创建Flask应用实例
app = create_app()

# 主程序入口
if __name__ == '__main__':
    # 启动开发服务器，监听5000端口
    app.run(port=5001)

## app/__init__.py
import os
import logging
from flask import Flask, render_template
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import Config

# 应用工厂函数
# 参数: config_class - 配置类，默认为Config
# 返回: 配置完成的Flask应用实例
def create_app(config_class=Config):
    # 创建Flask应用实例，启用实例相对配置
    app = Flask(__name__, instance_relative_config=True)
    
    # 从配置类加载配置
    app.config.from_object(config_class)
    
    # 确保实例文件夹存在
    os.makedirs(app.instance_path, exist_ok=True)
    
    # 初始化各组件
    _configure_logging(app)          # 配置日志系统
    _initialize_extensions(app)      # 初始化扩展(数据库、MQTT等)
    _register_blueprints(app)         # 注册蓝图
    _add_core_routes(app)             # 添加核心路由
    _validate_initialization(app)     # 验证初始化状态
    
    return app

# 配置应用日志系统
# 参数: app - Flask应用实例
def _configure_logging(app):
    # 非调试模式下配置日志文件
    if not app.debug:
        # 创建日志目录
        os.makedirs(Path(app.instance_path) / 'logs', exist_ok=True)
        
        # 设置日志文件处理器(最大10MB，保留5个备份)
        file_handler = RotatingFileHandler(
            Path(app.instance_path) / 'logs' / 'app.log', 
            maxBytes=10*1024*1024, 
            backupCount=5
        )
        
        # 设置日志格式
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    # 设置日志级别
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application logging initialized')

# 初始化应用扩展
# 参数: app - Flask应用实例
def _initialize_extensions(app):
    with app.app_context():
        # 初始化数据库
        from app.db.database import init_db
        init_db(app)
        
        # 初始化MQTT客户端
        from app.mqtt.client import MQTTClient
        mqtt_client = MQTTClient()
        mqtt_client.init_app(app)
        app.extensions['mqtt'] = mqtt_client

# 注册蓝图
# 参数: app - Flask应用实例
def _register_blueprints(app):
    from app.api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

# 添加核心路由
# 参数: app - Flask应用实例
def _add_core_routes(app):
    # 首页路由
    @app.route('/')
    def index():
        return render_template('dashboard.html')
    
    # 健康检查路由
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

# 验证应用初始化状态
# 参数: app - Flask应用实例
def _validate_initialization(app):
    if 'mqtt' not in app.extensions:
        raise RuntimeError('MQTT extension failed')