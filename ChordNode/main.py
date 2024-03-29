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

@app.route('/pred_notif', methods=['POST'])
def predec_notif():
    data = request.get_json()
    node.set_pred(data)
    return "success"


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


def node_active():
    return node.active


@app.route('/lookup', methods=['GET'])
def lookup():
    if not node_active():
        abort(404)
    print("lookup from main "+ str(request.get_data()))

    data = request.get_json()
    print("lookup data " + str(data["key"]))
    key = data["key"]

    result = node.lookup(key)
    print("result=" + str(result.position) + "\n result data, position: " + str(result.position) + " --ip: " + str(result.ip))
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
    data = [request.get_json()]
    result = node.insert_data(data)
    return result


@app.route('/retrieve_data', methods=['GET'])
def btree_search_route_retrieve():
    if not node_active():
        abort(404)
    search_data = request.get_json()
    search_key = search_data['Education']
    result = node.retrieve_data(search_key)
    return result





@app.route('/backup_data', methods=['POST'])
def store_data_route():
    if not node_active():
        abort(404)

    data = request.get_json()
    node.btree.insert(data)
    node.btree.backup_data.add(data['Education'])

    return "Data from depart received from successor"


@app.route('/receive_data', methods=['POST'])
def receive_data_route():
    if not node_active():
        abort(404)
    btree_state_data = request.get_json()
    result = node.store_data(btree_state_data, True)
    return result




@app.route('/suc_depart',methods=['POST'])
def successor_depart():
    if not node_active():
        abort(404)
    data=request.get_json()
    node.successor_depart(data["suc_num"])
    return "node changed successor"
@app.route('/pred_depart',methods=['POST'])
def predecessor_depart():
    if not node_active():
        abort(404)
    data=request.get_json()
    node.predecessor_depart(data)
    return "node changed predecessor"


@app.route('/depart', methods=['POST'])
def depart():
    if not node_active():
        abort(404)
    global status
    status = node.active
    response = node.depart()
    return "node departed"




@app.route('/stabilization', methods=['GET'])
def stabilaz():
    if not node_active():
        abort(404)
    suc_alive()
    rout_alive()
    return "done"


def suc_alive():
    return node.stabilize(1)


def rout_alive():
    return node.stabilize(2)

if __name__ == '__main__':
    # scheduler = BackgroundScheduler()
    # scheduler.start()
    # scheduler.add_job(suc_alive, 'interval', seconds=20)
    # scheduler.add_job(rout_alive, 'interval', seconds=70)
    app.run(host='0.0.0.0', port=5000)
