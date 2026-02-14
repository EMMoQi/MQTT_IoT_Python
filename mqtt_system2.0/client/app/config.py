# 导入必要的模块
import os
from pathlib import Path

# 应用配置类，包含应用运行所需的各种配置参数
class Config:
    # 获取当前文件所在目录的父目录作为基础目录
    BASE_DIR = Path(__file__).parent.parent
    # 明确指定数据库文件的绝对路径
    DATABASE = str(BASE_DIR / 'instance' / 'app.db')  # ✅ 改名为 DATABASE
    # MQTT 代理的 URL
    MQTT_BROKER_URL = 'localhost'
    # MQTT 代理的端口号
    MQTT_BROKER_PORT = 1883
    # MQTT 客户端的 ID
    MQTT_CLIENT_ID = 'flask_client'
    # MQTT 主题配置，包含客户端数据和服务器数据的主题
    MQTT_TOPICS = {
        'client_data': 'client/data',
        'server_data': 'server/data'
    }