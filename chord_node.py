
import random
import time

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
loger = ChordNodeLog()


class ChordNode:

    def __init__(self, size):

        self.chord_size: int = size
        self.successor_num = int(math.log2(self.chord_size))
        self.ip = helper.get_ip()
        self._position: int = helper.hash(self.ip, self.chord_size)
        temp_self_route = Routes(self.position, self.ip)
        self.predecessors: List[Routes] = [temp_self_route] * self.successor_num
        self.successors: List[Routes] = [temp_self_route] * self.successor_num
        self.routing_table: List[Routes] = [temp_self_route] * self.successor_num
        self.btree: BTree = BTree(False)
        print("ip:" + str(self.ip)
              + "\nposition:" + str(self.position)
              + "\n")

    @property
    def position(self) -> int:
        return self._position


    def bootstrap(self, data):
        # get data
        host = data
        domain = "/insertnode"

        # send request
        response = requests.get(host + domain, json={"ip": self.ip, "pos": self.position})
        #self.log("bootstrap to "+data)
        data = response.content
        self.get_init_data(data)

        nodes = helper.lookup_back_references(helper.get_back_references(self), self)
        for node in nodes.union({r.ip for r in (self.successors + self.predecessors)}):
            if node != self.ip:
                self.inform_node(node,1)


        btree_filename = f"cont_data/state_{self.ip.replace('.', '_').replace(':', '_')}.pkl"
        self.btree.load_state(btree_filename)
        loger.log_routes(self)
        time.sleep(0.25)
        print("\n\n\n\n\n\n.")
        return data

    def init(self, data):


        new_node_ip = data["ip"]
        new_node_position = data["pos"]



        new_node_successors = helper.get_successors(new_node_position, self)
        new_node_predecessors = helper.get_predecessor(new_node_position, self)
        if self.successors[0].position == self.position:
            for i in range(len(self.successors)):
                self.successors[i] = Routes(new_node_position, new_node_ip)
            for i in range(len(self.predecessors)):
                self.predecessors[i] = Routes(new_node_position, new_node_ip)
            for i in range(len(self.routing_table)):
                self.routing_table[i] = Routes(new_node_position, new_node_ip)
        json_successors=json.dumps(new_node_successors,default=Routes.serialize_routes,indent=2)
        json_predecessors = json.dumps(new_node_predecessors, default=Routes.serialize_routes, indent=2)
        data_to_send = {"successors": json_successors,
                        "predecessors": json_predecessors}

        data= json.dumps(data_to_send)
        #response = requests.post("http://"+new_node_ip + domain, json.dumps(data_to_send))
        #self.log("init " + new_node_ip)

        return data

    def get_init_data(self, data):
        print(data)
        data = json.loads(data)

        tmp = json.loads(data["successors"])
        self.successors = Routes.deserialize_routes(tmp)
        tmp = json.loads(data["predecessors"])
        self.predecessors = Routes.deserialize_routes(tmp)
        for i in range(len(self.routing_table)):
            self.routing_table[i] = self.successors[0]
        print("log1")
        loger.log_routes(self)
        print("log2")
        self.routing_table = self.make_routing_table()

        #self.log("get_init_data")
        return "self.routing_table"
    def lookup(self, key: int):
        key = key % self.chord_size  # to be sure that the key is inside the chord bounds
        print("lookup key:" + str(key) + " by node with  pos:" + str(self.position))
        for suc in self.successors:
            if helper.is_between(self.position, suc.position, key, self.chord_size) or suc.position == key:
                return suc

        for r in self.routing_table:
            f=self.position
            s=r.position
            if helper.is_between(f, s, key, self.chord_size) or suc.position == key:
                response = requests.get("http://" + r.ip + "/lookup", json={"key": key})
                data = json.loads(response.content.decode('utf-8'))
                return Routes(data["position"], data["ip"])
        return Routes(self.position, self.ip)

    def insert_data(self, data):

        for edu in data["Education"]:
            key = helper.hash(edu, self.chord_size)
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

        for data in search_key:
            target_node = self.lookup(helper.hash(data, self.chord_size))

            if target_node.ip == self.ip:
                if not hasattr(self, 'btree'):
                    return "B-tree is not initialized"

                matches = self.btree.search(data)

                search_results = []
                for node, index in matches:
                    search_results.append(node.keys[index])

                if search_results:
                    return jsonify(search_results)
                else:
                    return "No data found"
            else:
                target_node_ip = "http://" + target_node.ip + "/retrieve_data"
                response = requests.get(target_node_ip, json={"Education": data})
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

    def inform_node(self, node_ip: str, s: int):
        domain = "/inform"
        print("inform sent to" + str(node_ip))
        response = requests.post("http://" + node_ip + domain,json={"type": s})

        return response

    def handle_inform(self, node_ip: str, s :int):

        node_position = helper.hash(node_ip, self.chord_size)
        print("handle inform" + str(node_position))
        if s == 1: #node entering the ring
            ## add node to routing

            for i in range(len(self.successors)):
                if (i > 0) and (self.successors[i - 1].position == self.successors[i].position) and (helper.is_between(self.successors[i].position, self.position, node_position, self.chord_size)):
                    print("if cond in line 214 met")
                    for j in range(len(self.successors)):
                        self.successors.insert(j, Routes(node_position, node_ip))
                        self.successors.pop()
                    break
                if helper.is_between(self.position, self.successors[i].position, node_position, self.chord_size):


                    if i > 0 and self.successors[i - 1].position == node_position:
                        return
                    print("geting node" + str(node_position) + " in suc place:" + str(i) +
                          "pos:" + str(self.position) + " suc_pos" + str(self.successors[i].position))
                    self.successors.insert(i, Routes(node_position, node_ip))
                    self.successors.pop()


            for i in range(len(self.predecessors)):
                if helper.is_between(self.predecessors[i].position, self.position, node_position, self.chord_size):
                    print("geting node" + str(node_position) + " in pre place:" + str(i))
                    self.predecessors.insert(i, Routes(node_position, node_ip))
                    self.predecessors.pop()

            if self.routing_table[0].position > node_position:
                return 'error'
            for i in range(len(self.routing_table)):

                if self.position == self.routing_table[i].position or (helper.is_between(self.position+(2^i), self.routing_table[i].position,node_position,self.chord_size)):
                    tmp = Routes(node_position, node_ip + ':5000')
                    self.routing_table[i] = tmp
                    print("geting node" + str(node_position) + " in routing table place:" + str(i))





        else: #node exiting ring
            ##remove node from routing
            for i in range(len(self.routing_table)):
                if self.routing_table[i].position == node_position:
                    self.routing_table[i] = self.lookup(node_position - 1)
        loger.log_routes(self)
        print("__________________\n AFTER")
    def handle_post(self, data):
        data = request.get_data(as_text=True)
        name = self.ip
        print("url \' / \' invoked with data: " + name)
        file = open("/log/log.txt", 'a')
        file.write(name + "\n")

        return name

    def make_routing_table(self):
        table = []

        for i in range(len(self.routing_table)) :
            result = self.lookup((2 ** i) + (self.position))
            table.append(result)
            i = i + 1
        return table

    def is_alive(self):
        # Check if the next successor is alive
        next_successor_ip = self.lookup(self.position + 1).json()["ip"]
        next_successor_response = requests.post(f"http://{next_successor_ip}")
        if next_successor_response.status_code != 200:
            return "rebuild table"
        return "alive"

