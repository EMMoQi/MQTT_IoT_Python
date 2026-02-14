# routes.py
from flask import Blueprint, render_template, jsonify
from ..db.models import get_all_status, get_message_history

api_bp = Blueprint('api', __name__, template_folder='templates')


@api_bp.route('/current_status')  # ✅ 不要有 /api 前缀
def current_status():
    data = get_all_status()
    return jsonify([{
        'id': row[0],
        'temperature': row[1],
        'voltage': row[2],
        'last_updated': row[3]
    } for row in data])

@api_bp.route('/message_history')  # ✅ 不要有 /api 前缀
def message_history():
    data = get_message_history(limit=50)

    # 打印原始数据到终端（调试用）
    print("\n=== 原始数据 data ===")
    print("类型:", type(data))  # 打印数据类型
    print("内容:")
    for i, row in enumerate(data, 1):
        print(f"行 {i}: {row}")
    
    return jsonify([{
        'device_id': row['device_id'],
        'topic': row['topic'],
        'temperature': row['temperature'],
        'voltage': row['voltage'],
        'timestamp': row['timestamp']
    } for row in data])

