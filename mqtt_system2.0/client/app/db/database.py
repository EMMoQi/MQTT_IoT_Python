# 导入必要的模块
import sqlite3
from pathlib import Path

# 初始化数据库的函数
# :param app: Flask 应用实例，用于获取数据库路径配置
def init_db(app):
    # 确保数据库文件所在目录存在
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True)
    # 连接到数据库
    conn = sqlite3.connect(app.config['DATABASE'])
    # 创建游标对象
    c = conn.cursor()

    # 创建设备状态表，如果表不存在的话
    c.execute('''CREATE TABLE IF NOT EXISTS device_status (
        id TEXT PRIMARY KEY,
        temperature REAL,
        voltage REAL,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # 创建消息历史表，如果表不存在的话
    c.execute('''CREATE TABLE IF NOT EXISTS message_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        temperature REAL,
        voltage REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL
    )''')

    c.execute('''INSERT INTO test (device_id) VALUES ('haihai')''')

    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print("现有表:", [t[0] for t in tables])

    # 提交事务
    conn.commit()
    # 关闭数据库连接
    conn.close()

