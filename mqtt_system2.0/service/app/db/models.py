# 导入必要的模块
import sqlite3
from flask import current_app

# 更新设备状态的函数
# :param device_id: 设备 ID
# :param temp: 设备温度
# :param volt: 设备电压
def update_status(db_path, device_id, topic, temperature, voltage):
    conn = sqlite3.connect(current_app.config['DATABASE'])
    #conn = sqlite3.connect(db_path)
    #conn = sqlite3.connect('D:/miaoproj/mqtt_system2.0/service/instance/app.db')
    c = conn.cursor()
    
    # 更新当前状态
    c.execute('''
        INSERT INTO device_status (id, temperature, voltage, last_updated)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            temperature=excluded.temperature,
            voltage=excluded.voltage,
            last_updated=CURRENT_TIMESTAMP
    ''', (device_id, temperature, voltage))
    
    # 记录消息历史
    c.execute('''
        INSERT INTO message_history (device_id, topic, temperature, voltage)
        VALUES (?, ?, ?, ?)
    ''', (device_id, topic, temperature, voltage))
    
    conn.commit()
    conn.close()

# 获取所有设备状态的函数
# :return: 包含所有设备状态的列表
def get_all_status():
    # 连接到数据库
    conn = sqlite3.connect(current_app.config['DATABASE'])
    # 创建游标对象
    c = conn.cursor()
    # 查询所有设备状态数据
    c.execute('SELECT * FROM device_status')
    # 获取查询结果
    result = c.fetchall()
    # 关闭数据库连接
    conn.close()
    return result

# 获取消息历史记录的函数
# :param limit: 返回记录的最大数量，默认为 100
# :return: 包含消息历史记录的列表
import sqlite3
from flask import current_app

def get_message_history(limit=100):
    # 使用统一的配置路径连接到数据库
    conn = sqlite3.connect(current_app.config['DATABASE'])  # 确保你在 config.py 中配置了 DATABASE
    cursor = conn.cursor()

    # 查询历史消息记录
    cursor.execute('''
        SELECT device_id, topic, temperature, voltage, timestamp
        FROM message_history
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()

    print(f"查询到的条数: {len(rows)}")
    for row in rows:
        print(row)

    return [
        {
            'device_id': row[0],
            'topic': row[1],
            'temperature': float(row[2]),
            'voltage': float(row[3]),
            'timestamp': row[4]
        }
        for row in rows
    ]

