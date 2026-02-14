# MQTT_IoT_Python

Project Overview
MQTT System 2.0 is a real-time distributed messaging system built with Python and MQTT protocol.
It simulates a multi-client architecture where one client acts as a server node, supporting:

- Bidirectional publish/subscribe communication
- Real-time state synchronization
- Persistent state storage using SQLite
- Web-based visualization dashboard
- System upgrade package mechanism
- Continuous live message logging in terminal

This project focuses on real-time data transmission, state consistency, and clean system architecture design.


Project Structure
mqtt_system2.0/
├── client/
│ ├── app/
| | ├── api/
| | ├── db/
| | ├── mqtt/
| | ├── web/
| | ├── _init_.py
| | └── config.py
| ├── instance/
| | ├── logs/
| | ├── app.db
| | └── config.db
| ├── requirements.txt
│ └── run.py
├── service/
│ ├── app/
| | ├── api/
| | ├── db/
| | ├── mqtt/
| | ├── web/
| | ├── _init_.py
| | └── config.py
| ├── instance/
| | ├── logs/
| | ├── app.db
| | └── config.db
| ├── requirements.txt
│ └── run.py
└── DATABASE


System Architecture
Client A  ←→
              \
               →  MQTT Broker  →  Server Client (State Manager + Database)
              /
Client B  ←→


Components
- MQTT Broker
- Server Client
  - Manages global system state
  - Updates SQLite database
  - Publishes updated states
- Client A & Client B
  - Publish structured data
  - Subscribe to state updates
- SQLite Database
  - Stores only current device states (not historical logs)
- Web Frontend
  - Displays real-time system state
  - Automatically refreshes from backend data


Technologies Used
- Python
- MQTT (paho-mqtt)
- SQLite
- HTML / CSS / JavaScript
- JSON message structures


Features
1. Real-Time Bidirectional Messaging
- Clients publish structured data
- Server processes and republishes state
- Supports QoS configuration
- Continuous message flow between all nodes

2. State-Based Database Design (Optimized)
Unlike traditional message-logging systems:
- No historical message storage
- Only latest client state stored
- Database always reflects current system snapshot
This improves: Performance, Clarity, System scalability

3. Structured Message Format
Messages support multiple data structures:
- Device status
- Control commands
- System update notifications
- Upgrade packages
- All messages use structured JSON payloads.

4. System Upgrade Package Mechanism
- Server can publish system update messages
- Clients receive upgrade instructions
- Simulates OTA-style update logic

5. Real-Time Terminal Logging
Each client continuously prints:
- Published messages
- Received messages
- Database update status
- System events
Helps debugging and monitoring.

6. Web Visualization Interface
- Displays live client status
- Shows current state stored in database
- Clean and responsive layout
- Automatically reflects backend updates


Database Design
SQLite table stores:
- Client ID	Status	Data	Last Updated
- Important design choice: The database stores only current state, not historical logs.
  This ensures: Lightweight storage, Clear system snapshot, Faster queries


Design Highlights
- Event-driven architecture
- Decoupled publish/subscribe design
- Separation of communication layer and storage layer
- Real-time consistency model
- Upgrade-ready system structure


How to Run
1. Install dependencies
```bash
pip install paho-mqtt
```

2. Start MQTT Broker
Example using Mosquitto:
```bash
mosquitto
```

4. Run Server Client
python server.py

5. Run Client A / Client B
python client_a.py
python client_b.py

6. Open Web Interface
Open index.html in browser.


Project Purpose
This project was built to:
- Practice distributed system communication
- Understand MQTT architecture deeply
- Implement state synchronization logic
- Combine backend, database, and frontend in one system
- Simulate real-world IoT communication patterns


Future Improvements
- Add authentication & security layer
- Add historical logging mode (optional)
- Docker deployment
- WebSocket integration
- Cloud deployment support


Author
Emily Miao
Computer Science Student
