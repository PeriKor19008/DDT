import json

from chord_node import ChordNode, request
from flask import Flask, jsonify, abort
from routes import Routes
import logging
from apscheduler.schedulers.background import BackgroundScheduler




app = Flask(__name__)

node = ChordNode(16)
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(logging.StreamHandler())
@app.route('/bootstrap', methods=['POST'])
def bootstrap():
    logging.debug('bootstrap')
    data = request.get_data(as_text=True)
    return node.bootstrap(data)

# @app.route('/insertnode', methods=['GET'])
# def init():
#     data = request.get_json()
#     return node.init(data)


@app.route('/get_succ', methods=['GET'])
def get_suc():
    data = request.get_json()
    return node.get_succ(data)

@app.route('/get_predecessor', methods=['GET'])
def get_pre():
    pre_ip = node.predecessor.ip
    pre_pos = node.predecessor.position
    data = jsonify({"ip": pre_ip, "pos": pre_pos})
    return data

@app.route('/new_predecessor', methods=['GET'])
def new_pred():

    data = request.get_json()
    result = node.new_predecessor(data)
    return result
@app.route('/new_successor', methods=['POST'])
def new_suc():

    data = request.get_json()
    result = node.new_successor(data)
    return result

@app.route('/ping', methods=['POST'])
def ping():

    result = node.is_alive()
    return result

def node_active():
    return node.active


@app.route('/init_data', methods=['POST'])
def get_init_data():
    if not node_active():
        abort(404)
    data = request.get_data(as_text=True)
    return node.get_init_data(data)


@app.route('/', methods=['POST'])
def handle_post():
    if not node_active():
        abort(404)
    data = request.get_data(as_text=True)
    return node.handle_post(data)


@app.route('/lookup', methods=['GET'])
def lookup():
    if not node_active():
        abort(404)
    print("lookup from main "+ str(request.get_data()))

    data = request.get_json()
    print("lookup data " + str(data["key"]))
    key = data["key"]

    result = node.lookup(key)
    print("result=" + str(result) + "\n result data, position: " + str(result.position) + " --ip: " + str(result.ip))
    if not isinstance(result, Routes):
        return result
    return jsonify({"position": result.position, "ip": result.ip})


@app.route('/show_routes', methods=['POST'])
def show_routes():
    if not node_active():
        abort(404)
    node.log()
    return"log"


@app.route('/insert_data', methods=['POST'])
def btree_insert_route():
    if not node_active():
        abort(404)
    data = request.get_json()
    result = node.store_data(data,True)
    return result


@app.route('/retrieve_data', methods=['GET'])
def btree_search_route_retrieve():
    if not node_active():
        abort(404)
    search_data = request.get_json()
    search_key = search_data['Education']
    result = node.retrieve_data(search_key)
    return result


@app.route('/search_data', methods=['GET'])
def btree_search_route_search():
    if not node_active():
        abort(404)
    search_data = request.get_json()
    search_key = search_data['Education']
    result = node.search_data(search_key)
    return result


@app.route('/delete_data', methods=['GET'])
def delete_data_from_btree():
    if not node_active():
        abort(404)
    data = request.get_json()
    for d in data:
        node.btree.delete(node.btree.root, d['Education'])
    return "data deleted"


@app.route('/backup_data', methods=['POST'])
def store_data_route():
    if not node_active():
        abort(404)
    data = [request.get_json()]
    if len(data) > 0:
        for item in data:
            node.btree.insert(item)
    # node.btree.print_tree(node.btree.root)
    return "Data from depart received from successor"


@app.route('/receive_data', methods=['POST'])
def receive_data_route():
    if not node_active():
        abort(404)
    btree_state_data = request.get_json()
    result = node.store_data(btree_state_data, True)
    return result


@app.route('/inform',methods=['POST'])
def receive_inform():
    if not node_active():
        abort(404)
    print("inform")
    data=request.get_json()
    return jsonify(node.handle_inform(request.remote_addr +":5000/", data['pos'] , data['type']))


@app.route('/depart', methods=['POST'])
def depart():
    if not node_active():
        abort(404)
    global status
    status = node.active
    response = node.inform_node(request.remote_addr +":5000/", 2)
    return response

@app.route('/print_tree', methods=['GET'])
def print_tree():
    node.btree.print_tree(node.btree.root)
    return "\n\nBtree Data\n\n"

def suc_alive():
    return node.stabilize(1)


def rout_alive():
    return node.stabilize(2)



if __name__ == '__main__':
    # scheduler = BackgroundScheduler()
    # scheduler.start()
    # scheduler.add_job(suc_alive, 'interval', seconds=2)
    # scheduler.add_job(rout_alive, 'interval', seconds=7)
    app.run(host='0.0.0.0', port=5000)