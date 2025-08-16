from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import json
from my_mqtt_client import My_Mqtt

vm_mqtt_client=My_Mqtt()
vm_mqtt_client.run()

app = Flask(__name__)
@app.route('/publish/', methods=['POST'])
def publish():
    global vm_mqtt_client
    try:
        data = request.get_json(force=True)   
        print(type(data))
        print(data)
        
        topic = data.get("topic")
        message = data.get("message")
        
        if not topic or message is None:
            return jsonify({"error": "Missing 'topic' or 'message'"}), 400

        if vm_mqtt_client.is_connected():
            vm_mqtt_client.publish_message(topic, message)
            return jsonify({"status": "published", "topic": topic}), 200
        else:
            return jsonify({"error":"not connect to broker"}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
