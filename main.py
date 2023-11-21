from CHORD import Chord_node
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/bootstrap', methods=['POST'])
def bootstrap():
    data = request.get_data(as_text=True)
    host='http://127.0.0.1:5001/init'
    response= requests.post(host,"peri init")
    return response

@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_data(as_text=True)
    return data

@app.route('/insertnode', methods=['POST'])
def init():
    data = request.get_data(as_text=True)
    return data+"init"

if __name__ == '__main__':
    node = Chord_node.node_init()
    print("node ready")
    app.run(host='0.0.0.0', port=5000)





