from chord_node import ChordNode
from flask import Flask, request


app = Flask(__name__)

node = ChordNode(16)

@app.route('/initialize', methods=['POST'])
def initialize():
    flask_ip = request.remote_addr
    return node.initialize(flask_ip)

@app.route('/first', methods=['POST'])
def first():
    return node.first()

@app.route('/join', methods=['POST'])
def join():
    data = request.get_data(as_text=True)
    return node.join(data)

@app.route('/receive_info', methods=['POST'])
def receive_info():
    data = request.get_json()
    info = data["pos"]
    print("Received data:", data)
    return node.receive_info(info)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)