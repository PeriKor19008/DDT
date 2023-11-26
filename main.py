from CHORD_test import Chord_node
from flask import Flask, request, make_response
import requests

app = Flask(__name__)

@app.route('/bootstrap', methods=['POST'])
def bootstrap():
    data = request.get_data(as_text=True)
    print("bootstrap invoked with data:"+data)

    responce = requests.post(data,"data sent by bootstrap")
    print("data sent to container by bootstrap \n")
    return data
@app.route('/', methods=['POST'])
def handle_post():

    data = request.get_data(as_text=True)
    print("url \' / \' invoked with data: "+ data)
    return data

@app.route('/insertnode', methods=['POST'])
def init():
    data = request.get_data(as_text=True)
    return data+"init"

if __name__ == '__main__':
    node = Chord_node.node_init()
    print("node ready")
    app.run(host='0.0.0.0', port=5000)





