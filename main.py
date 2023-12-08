from chord_node import ChordNode,request
from flask import Flask
import json

app = Flask(__name__)

node = ChordNode(16)
@app.route('/bootstrap', methods=['POST'])
def bootstrap():
    data = request.get_data(as_text=True)
    return node.bootstrap(data)

@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_data(as_text=True)
    return node.handle_post(data)

@app.route('/lookup', methods=['POST'])
def lookup():
    data = json.loads(request.get_data())
    key = data("key")
    return node.lookup(key)

@app.route('/insertnode', methods=['POST'])
def init():
    data = request.get_data(as_text=True)
    return node.init(data)

@app.route('/init_data', methods=['POST'])
def get_init_data():
    data = request.get_data(as_text=True)
    return node.get_init_data(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



