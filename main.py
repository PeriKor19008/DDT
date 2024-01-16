import time

from chord_node import ChordNode, request
from flask import Flask, jsonify
import json
import threading
from routes import Routes
import logging




app = Flask(__name__)

node = ChordNode(16)

app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logging.StreamHandler())
@app.route('/bootstrap', methods=['POST'])
def bootstrap():
    logging.debug('bootstrap')
    data = request.get_data(as_text=True)
    return node.bootstrap(data)

@app.route('/init_data', methods=['POST'])
def get_init_data():
    data = request.get_data(as_text=True)
    return node.get_init_data(data)


@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_data(as_text=True)
    return node.handle_post(data)

@app.route('/lookup', methods=['GET'])
def lookup():
    print("lookup from main "+ str(request.get_data()))
    time.sleep(1)
    data = request.get_json()
    print("lookup data " + str(data["key"]))
    key = data["key"]

    result = node.lookup(key)
    print("result=" + str(result) + "\n result data, position: " + str(result.position) + " --ip: " + str(result.ip))
    if not isinstance(result, Routes):
        return result
    return jsonify({"position": result.position, "ip": result.ip})

@app.route('/insertnode', methods=['GET'])
def init():
    data = request.get_json()
    return node.init(data)



@app.route('/ping', methods=['POST'])
def ping():

    result = node.is_alive()
    return result
@app.route('/show_routes', methods=['POST'])
def show_routes():
    return node.log_routes()

@app.route('/insert_data', methods=['POST'])
def btree_insert_route():
    data = request.get_json()
    result = node.insert_data(data)
    return result

@app.route('/retrieve_data', methods=['GET'])
def btree_search_route_retrieve():
    search_data = request.get_json()
    search_key = search_data['Education']   
    result = node.retrieve_data(search_key)
    return result

@app.route('/search_data', methods=['GET'])
def btree_search_route_search():
    search_data = request.get_json()
    search_key = search_data['Education']
    result = node.search_data(search_key)
    return result

@app.route('/store_data', methods=['POST'])
def store_data_route():
    btree_state_data = request.data
    result = node.store_data()
    return result

@app.route('/receive_data', methods=['POST'])
def receive_data_route():
    btree_state_data = request.data
    btree_filename = request.args.get('filename')
    with open(btree_filename, 'wb') as file:
        file.write(btree_state_data)

@app.route('/inform',methods=['POST'])
def receive_inform():
    print("inform")
    data=request.get_json()
    return jsonify(node.handle_inform(request.remote_addr +":5000/", data['type']))


def schedule_ping():
    while True:
        # calls ping every 5 seconds
        timer = threading.Timer(5, ping)
        timer.start()
        timer.join()

if __name__ == '__main__':
    # ping_thread = threading.Thread(target=schedule_ping)
    # ping_thread.start()

    app.run(host='0.0.0.0', port=5000)