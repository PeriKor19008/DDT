from chord_node import ChordNode,request
from flask import Flask, jsonify
import json
import threading
from routes import Routes

app = Flask(__name__)

node = ChordNode(16)
@app.route('/bootstrap', methods=['POST'])
def bootstrap():
    data = request.get_data(as_text=True)
    return node.bootstrap(data)

@app.route('/init_data', methods=['POST'])
def get_init_data():
    print("aaaaamain")
    data = request.get_data(as_text=True)
    return node.get_init_data(data)


@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_data(as_text=True)
    return node.handle_post(data)

@app.route('/lookup', methods=['POST'])
def lookup():
    data = request.get_json()
    key = data["key"]

    return jsonify(Routes.serialize_routes(node.lookup(key)))

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
    data=request.get_json()
    return node.handle_inform(request.remote_addr ,data['type'])


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