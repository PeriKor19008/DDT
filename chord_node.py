
import random
from b_tree_new import BTree
from flask import request,  jsonify
import requests
import json
from routes import Routes
from typing import List
import math
from chord_node_helper import ChordNodeHelper
from chord_node_log import ChordNodeLog


helper = ChordNodeHelper()
loger = ChordNodeLog


class ChordNode:

    def __init__(self, size):

        self.chord_size: int = size
        self.successor_num = int(math.log2(self.chord_size))
        self.ip = helper.get_ip()
        temp_self_route = Routes(-1, self.ip)
        self.predecessors: List[Routes] = [temp_self_route]
        self.successors: List[Routes] = [temp_self_route]
        self.routing_table: List[Routes] = None
        self.btree: BTree = BTree(False)
        self.position: int



    def bootstrap(self, data):
        # get data
        host = data
        domain = "/insertnode"
        print("bbbbbbb")
        # send request
        response = requests.get(host + domain, json={"ip": self.ip})
        #self.log("bootstrap to "+data)
        data = response.content
        self.get_init_data(data)

        nodes = helper.lookup_back_references(helper.get_back_references(self), self)

        for node in nodes:
            self.inform_node(node,1)

        btree_filename = f"cont_data/state_{self.ip.replace('.', '_').replace(':', '_')}.pkl"
        self.btree.load_state(btree_filename)
        return data

    def init(self, data):


        new_node_ip = data["ip"]
        new_node_position = helper.hash_ip(new_node_ip, self.chord_size)

        new_node_successors = helper.get_successors(new_node_position, self)
        new_node_predecessors = helper.get_predecessor(new_node_position, self)

        json_successors=json.dumps(new_node_successors,default=Routes.serialize_routes,indent=2)
        json_predecessors = json.dumps(new_node_predecessors, default=Routes.serialize_routes, indent=2)
        data_to_send = {"position": new_node_position,
                        "successors": json_successors,
                        "predecessors": json_predecessors}

        data= json.dumps(data_to_send)
        #response = requests.post("http://"+new_node_ip + domain, json.dumps(data_to_send))
        #self.log("init " + new_node_ip)

        return data

    def get_init_data(self, data):
        print("aaaaaaaa")
        data = json.loads(data)

        tmp = json.loads(data["successors"])
        self.successors = Routes.deserialize_routes(tmp)
        tmp = json.loads(data["predecessors"])
        self.predecessors = Routes.deserialize_routes(tmp)
        self.position = data.get("position")

        self.routing_table = self.make_routing_table()
        print(self.routing_table)
        #self.log("get_init_data")
        return "self.routing_table"
    def lookup(self, key: int):
        print(key)
        closest_successor = helper.lookup_inner(key,self)
        if closest_successor[1]:
            return closest_successor[0]
        ip = "http://" + closest_successor[0].ip + "lookup"
        data_to_send = {"key": key}
        response = requests.post(ip, json={"key": key})
        # self.log("lookup")

        return response

    def insert_data(self, data):

        key = data['Education']
        target_node = self.lookup(key)

        if target_node.ip == self.ip:
            if not hasattr(self, 'btree'):
                t = 3
                self.btree = BTree(t)
            self.btree.insert(data)
            return "Data inserted successfully"
        else:
            target_node_ip = "http://" + target_node.ip + "/insert_data"
            requests.post(target_node_ip, json=data)
            return "Data sent to the appropriate node for insertion"

    def retrieve_data(self, search_key):
        target_node = self.lookup(search_key)

        if target_node.ip == self.ip:
            if not hasattr(self, 'btree'):
                return "B-tree is not initialized"

            matches = self.btree.search(search_key)

            search_results = []
            for node, index in matches:
                search_results.append(node.keys[index])

            if search_results:
                return jsonify(search_results)
            else:
                return "No data found"
        else:
            target_node_ip = "http://" + target_node.ip + "/retrieve_data"
            response = requests.get(target_node_ip, json={"Education": search_key})
            return response.text

    def search_data(self, search_key):

        if not hasattr(self, 'btree'):
            return "B-tree is not initialized"

        matches = self.btree.search(search_key)
        search_results = []
        for node, index in matches:
            search_results.append(node.keys[index])

        if search_results:
            return jsonify(search_results)
        else:
            return "No matching data found"

    def store_data(self):
        btree_filename = f"cont_data/state_{self.ip.replace('.', '_').replace(':', '_')}.pkl"
        self.btree.save_state(btree_filename)
        selected_nodes = random.sample(self.routing_table, min(2, len(self.routing_table)))

        for selected_node in selected_nodes:
            if selected_node.ip != self.ip:
                target_node_ip = "http://" + selected_node.ip + "/receive_data"
                with open(btree_filename, 'rb') as file:
                    btree_state_data = file.read()
                    requests.post(target_node_ip, data=btree_state_data,
                                  headers={'Content-Type': 'application/octet-stream'},
                                  params={'filename': btree_filename})
                    return "Data stored"

    def inform_node(self, node: Routes, s: int) -> None:
        domain = "inform"
        response = requests.post(node.ip + domain,json={"type": s})

    def handle_inform(self, node_ip: str, s :int):
        node_position = helper.hash_ip(node_ip, self.chord_size)
        if s == 1: #node entering the ring
            ##add node to routing


            if self.routing_table[0].position > node_position:
                return 'error'
            for i in range(len(self.routing_table)-1):
                if self.routing_table[i+1].position > node_position and self.position + 2 ^(i+1) > node_position:
                    tmp = Routes(node_position,node_ip + ':5000')
                    self.routing_table[i]=tmp


        else: #node exiting ring
            ##remove node from routing
            for i in range(len(self.routing_table)):
                if self.routing_table[i].position == node_position:
                    self.routing_table[i] = self.lookup(node_position - 1)

    def handle_post(self, data):
        data = request.get_data(as_text=True)
        name = self.ip
        print("url \' / \' invoked with data: " + name)
        file = open("/log/log.txt", 'a')
        file.write(name + "\n")

        return name

    def make_routing_table(self):
        table = []
        i=1
        while i<math.sqrt(self.chord_size) :
            result = self.lookup(i)
            table.append(result)
            i = i * 2
        return table

    def is_alive(self):
        # Check if the next successor is alive
        next_successor_ip = self.lookup(self.position + 1).json()["ip"]
        next_successor_response = requests.post(f"http://{next_successor_ip}")
        if next_successor_response.status_code != 200:
            return "rebuild table"
        return "alive"

