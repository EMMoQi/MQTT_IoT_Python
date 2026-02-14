import json
import time
import random
import threading
from datetime import datetime
import paho.mqtt.client as mqtt
from flask import current_app
from app.db.models import update_status

class MQTTClient:
    def __init__(self):
        """初始化MQTT客户端"""
        self.client = None
        self.app = None  # ✅ 新增
        self.connection_status = False
        self.last_message_time = None
        self._stop_event = threading.Event()  # 用于优雅停止线程

    def init_app(self, app):
        """初始化应用上下文中的MQTT客户端"""
        self.app = app  # ✅ 保存 app 实例
        self.client = mqtt.Client(
            client_id=app.config['MQTT_CLIENT_ID'],
            clean_session=True,
            protocol=mqtt.MQTTv311
        )
        
        # 配置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # 配置TLS（如果需要）
        # self.client.tls_set(ca_certs="ca.crt")
        
        try:
            # 连接broker
            self.client.connect(
                host=app.config['MQTT_BROKER_URL'],
                port=app.config['MQTT_BROKER_PORT'],
                keepalive=60
            )
            
            # 启动后台线程
            self.client.loop_start()
            
            # 启动数据广播线程
            broadcast_thread = threading.Thread(
                target=self._broadcast_loop,
                args=(app,),
                daemon=True
            )
            broadcast_thread.start()
            
            app.logger.info("MQTT client initialized successfully")
            
        except Exception as e:
            app.logger.error(f"MQTT connection failed: {str(e)}")
            raise

    def _on_connect(self, client, userdata, flags, rc):
        """连接回调函数"""
        with self.app.app_context():
            if rc == 0:
                self.connection_status = True
                current_app.logger.info("MQTT connected")
                
                # 订阅所有必要的主题
                topics = current_app.config['MQTT_TOPICS']
                for topic in [topics['client_data']]:  # 可以扩展更多主题
                    client.subscribe(topic, qos=1)
                    current_app.logger.info(f"Subscribed to {topic}")
                for topic in [topics['server_data']]:  # 可以扩展更多主题
                    client.subscribe(topic, qos=1)
                    current_app.logger.info(f"Subscribed to {topic}")
            else:
                error_codes = {
                    1: "不正确的协议版本",
                    2: "无效的客户端标识符",
                    3: "服务器不可用",
                    4: "错误的用户名或密码",
                    5: "未授权"
                }
                error_msg = error_codes.get(rc, f"未知错误({rc})")
                current_app.logger.error(f"Connection failed: {error_msg}")

    def _on_message(self, client, userdata, msg):
        """消息接收回调函数"""
        with self.app.app_context():
            try:
                payload = msg.payload.decode('utf-8')
                current_app.logger.info(f"📩 [MQTT] Received on {msg.topic}: {payload}")
                self.last_message_time = datetime.now()
                
                current_app.logger.debug(
                    f"Received message on {msg.topic}: {payload[:100]}..."  # 限制日志长度
                )
                
                data = json.loads(payload)
                print(data)
                # 验证必要字段
                required_fields = {'temperature', 'voltage'}
                if not all(field in data for field in required_fields):
                    raise ValueError("Missing required fields")
                    
                # 更新数据库
                device_id = "client_" + msg.topic.split('/')[-1]  # 从主题提取设备ID
                update_status(
                    db_path=self.app.config['DATABASE'],
                    device_id=device_id,
                    topic=msg.topic,
                    temperature=float(data['temperature']),
                    voltage=float(data['voltage'])
                )
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Invalid JSON: {str(e)}")
            except ValueError as e:
                current_app.logger.error(f"Data validation failed: {str(e)}")
            except Exception as e:
                current_app.logger.error(f"Unexpected error: {str(e)}")

    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调函数"""
        with self.app.app_context():
            self.connection_status = False
            if rc != 0:
                current_app.logger.warning(f"Unexpected disconnection (rc={rc})")
        
        # 自动重连逻辑
        retry_count = 0
        while retry_count < 5 and not self._stop_event.is_set():
            try:
                current_app.logger.info(f"Attempting reconnect ({retry_count + 1}/5)")
                self.client.reconnect()
                return
            except Exception:
                retry_count += 1
                time.sleep(5)
        
        current_app.logger.error("Failed to reconnect after 5 attempts")

    def _broadcast_loop(self, app):
        """服务器数据广播线程"""
        with app.app_context():
            # 初始化模拟数据
            sim_data = {
                'temperature': 26.0,
                'voltage': 3.8,
                'status': 'normal'
            }
            
            while not self._stop_event.is_set():
                try:
                    # 生成随机波动
                    sim_data['temperature'] = round(
                        max(20.0, min(
                            sim_data['temperature'] + random.uniform(-0.5, 0.5),
                            35.0
                        )), 1
                    )
                    
                    sim_data['voltage'] = round(
                        max(3.0, min(
                            sim_data['voltage'] + random.uniform(-0.05, 0.05),
                            4.2
                        )), 2
                    )
                    
                    # 添加时间戳
                    sim_data['timestamp'] = datetime.now().isoformat()
                    
                    # 发布数据
                    payload = json.dumps(sim_data)
                    self.client.publish(
                        topic=app.config['MQTT_TOPICS']['server_data'],
                        payload=payload,
                        qos=1,
                        retain=False
                    )
                    current_app.logger.info(f"📤 [MQTT] Sent to {app.config['MQTT_TOPICS']['server_data']}: {payload}")
                    # 更新本地数据库
                    update_status(
                        db_path='DATABASE',
                        device_id='server',
                        topic='server_data',
                        temperature=sim_data['temperature'],
                        voltage=sim_data['voltage']
                    )
                    
                    current_app.logger.debug(f"Broadcast: {payload}")
                    
                    # 动态间隔（2-5秒）
                    time.sleep(2 + random.random() * 3)
                    
                except Exception as e:
                    current_app.logger.error(f"Broadcast error: {str(e)}")
                    time.sleep(5)

    def stop(self):
        """优雅停止客户端"""
        self._stop_event.set()
        self.client.disconnect()
        self.client.loop_stop()
        with self.app.app_context():
            current_app.logger.info("MQTT client stopped gracefully")

# 使用示例：
# mqtt_client = MQTTClient()
# mqtt_client.init_app(app)
# 在应用退出时调用：
# mqtt_client.stop()