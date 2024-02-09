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
        self.active = False
        self.successor_num = int(math.log2(self.chord_size))
        self.ip = helper.get_ip()
        self.position: int = helper.hash(self.ip, self.chord_size)
        temp_self_route = Routes(self.position, self.ip)
        self.successors: List[Routes] = [temp_self_route] * self.successor_num
        self.routing_table: List[Routes] = [temp_self_route] * self.successor_num
        self.predecessor: Routes = temp_self_route
        self.btree: BTree = BTree(False)
        print("ip:" + str(self.ip)
              + "\nposition:" + str(self.position)
              + "\n")


    def bootstrap(self, data):
        self.active = True
        host = data
        domain = "/insertnode"

        # send request
        # Loop the request and if the response has json with key: error it recalculates position
        while True:
            response = requests.get(host + domain, json={"ip": self.ip, "pos": self.position})
            # If the response returns the pres/sucs then it decodes it to check the keys
            content_str = response.content.decode('utf-8')
            content_json = json.loads(content_str)
            #self.log("bootstrap to "+data)
            if "error" in content_json:
                print("\n Position already taken, re-calculating position \n")
                self.position = helper.hash(self.ip, self.chord_size, True)

            else:
                print("\n Position OK \n")
                break
                
        data = response.content
        self.get_init_data(data)

        n = helper.get_back_references(self)
        nodes = helper.lookup_back_references(n, self)
        print("refrences" + str(nodes))
        for node in nodes:
            if node != self.ip:
                self.inform_node(node, 1)
        for r in self.successors:
            if r.ip != self.ip:
                self.inform_node(r.ip, 1)

        loger.log_routes(self)

        print("\n\n\n\n\n\n.")
        return data

    def init(self, data):
        self.active = True
        new_node_ip = data["ip"]
        new_node_position = data["pos"]
        
        # Checks if position already exists
        # Returns json with key:error
        collision_node = self.lookup(new_node_position)
        if collision_node.position == new_node_position:
            return {"error":"position"}

        
        new_node_successors = helper.get_successors(new_node_position, self)
        new_node_predecessor = helper.get_predecessor(new_node_position,self)

        if self.successors[0].position == self.position:
            for i in range(len(self.successors)):
                self.successors[i] = Routes(new_node_position, new_node_ip)

            for i in range(len(self.routing_table)):
                self.routing_table[i] = Routes(new_node_position, new_node_ip)
        if self.predecessor.position == self.position:
            self.predecessor = Routes(new_node_position, new_node_ip)


        json_successors = json.dumps(new_node_successors, default=Routes.serialize_routes, indent=2)
        json_predecessor = json.dumps(new_node_predecessor,default=Routes.serialize_routes, indent=2)
        data_to_send = {"successors": json_successors,
                        "predecessor": json_predecessor}

        data = json.dumps(data_to_send)
        return data

    def get_init_data(self, data):
        print(data)
        data = json.loads(data)

        tmp = json.loads(data["successors"])
        self.successors = Routes.deserialize_routes(tmp)
        tmp = json.loads(data["predecessor"])
        self.predecessor = Routes(tmp['position'], tmp['ip'])

        for i in range(len(self.routing_table)):
            self.routing_table[i] = self.successors[0]
        print("log1")
        loger.log_routes(self)
        print("log2")
        self.routing_table = self.make_routing_table()

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
            if helper.is_between(f, s, key, self.chord_size) or r.position == key:
                print("http://" + r.ip + "lookup\n\n\n\n")
                response = requests.get("http://" + r.ip + "lookup", json={"key": key})
                data = json.loads(response.content.decode('utf-8'))
                return Routes(data["position"], data["ip"])
        return Routes(self.position, self.ip)

    def insert_data(self, data):

        if isinstance(data, bytes):
            decoded_data = json.loads(data.decode('utf-8'))
            data = decoded_data.get("keys", [])

        for item in data:
            for edu in item["Education"]:
                key = helper.hash(edu, self.chord_size)
                target_node = self.lookup(key)

                if target_node.ip == self.ip:
                    if not hasattr(self, 'btree'):
                        t = 3
                        self.btree = BTree(t)
                    self.store_data(item,True)
                    return "Data inserted successfully"
                else:
                    target_node_ip = "http://" + target_node.ip + "/insert_data"
                    requests.post(target_node_ip, json=item)
                    return "Data sent to the appropriate node for insertion"

    def store_data(self, tree_data, send_to_suc):
        self.btree.insert(tree_data)
        if send_to_suc:
            keys = tree_data.get("Education", [])
            self.btree.owned(keys)
            result = self.backup_data(tree_data)
            return result
        return "Data stored"
    def backup_data(self, tree_data):
        for selected_node in self.successors:
            target_node_ip = "http://" + selected_node.ip + "/backup_data"
            requests.post(target_node_ip, json=tree_data,
                          headers={'Content-Type': 'application/json'})


        return "Data sent to Successors"

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


                   
    def inform_node(self, node_ip: str, s: int):
        domain = "/inform"
        if s==1:
            print("inform sent to " + str(node_ip))
            # Added to json another key: "pos"
            response = requests.post("http://" + node_ip + domain,json={"type": s, "pos": self.position})
            return response
        else:
            # Added argument: depart to split entering and departing
            
            n = helper.get_back_references(self)
            nodes = helper.lookup_back_references(n, self)
            self.active = False
            for j in nodes:
                if j != self.ip:
                    print("inform for depart sent to " + str(j))
                    response = requests.post("http://" + j + domain,json={"type": s, "pos": self.position})

            tmp = []
            if self.btree.owned_data:
                for data in self.btree.owned_data:
                    search_results = self.btree.search(data)
                    for node, index in search_results:
                        if index < len(node.keys):
                            tmp.append(node.keys[index])
                json_data = json.dumps(tmp)
                target_node_ip = "http://" + self.successors[0].ip + "/receive_data"
                requests.post(target_node_ip, json=json_data,
                            headers={'Content-Type': 'application/json'})

            return 'Node ' + str(self.position) + ' left the ring'
            

    def handle_inform(self, node_ip: str, node_position: int, s :int):
        
        # Removed hash because a node can have different position because of collisions.
        # Added another argument: node_position

        if s == 1: #node entering the ring
            ##add node to routing
            print("Entering: handle inform " + str(node_position))
            if helper.is_between(self.predecessor.position,self.position,node_position,self.chord_size):
                print("\n\n\n\n\nPRED")
                i = 1
                while True:
                    pre = self.lookup(self.predecessor.position-i)
                    if pre.position != node_position and pre.position != self.predecessor.position:
                        print("pre pos" + str(pre.position))
                        self.predecessor = pre
                        break
                    i = i + 1

            for i in range(len(self.successors)):
                if (i > 0) and (self.successors[i - 1].position == self.successors[i].position) and (helper.is_between(self.successors[i].position, self.position, node_position, self.chord_size)):
                    print("if cond in line 214 met")
                    for j in range(len(self.successors)):
                        self.successors.insert(j+1, Routes(node_position, node_ip))
                        self.successors.pop()
                    break
                if helper.is_between(self.position, self.successors[i].position, node_position, self.chord_size):


                    if i > 0 and self.successors[i - 1].position == node_position:
                        return
                    print("geting node" + str(node_position) + " in suc place:" + str(i) +
                          "pos:" + str(self.position) + " suc_pos" + str(self.successors[i].position))
                    self.successors.insert(i, Routes(node_position, node_ip))
                    if len(self.btree.root.keys) != 0: 
                        tmp = []
                        for data in self.btree.owned_data:
                            tmp.append(self.btree.search(data))
                        json_data = json.dumps(tmp)
                        target_node_ip = "http://" + node_ip + "/backup_data"
                        requests.post(target_node_ip, data=json_data,
                                    headers={'Content-Type': 'application/json'})
                        requests.get("http://" + self.successors[-1].ip +"delete_data", json=json_data,
                                    headers={'Content-Type': 'application/json'})
                    self.successors.pop()

            if self.routing_table[0].position > node_position:
                return 'error'
            for i in range(len(self.routing_table)):

                if self.position == self.routing_table[i].position or (helper.is_between(self.routing_table[i].position, self.position+(2 ^ i), node_position, self.chord_size)):
                    tmp = Routes(node_position, node_ip )
                    self.routing_table[i] = tmp
                    print("geting node" + str(node_position) + " in routing table place:" + str(i))


        else: #node exiting ring
            self.delete_node_from_routing(node_position)
                    
        loger.log_routes(self)
        print("__________________\n AFTER")

    def delete_node_from_routing(self,node_position: int):
        print("find new successors")
        for i in range(len(self.successors)):
            if self.successors[i].position == node_position:
                    self.successors[i] = self.lookup(self.successors[i].position + 1)

        i_values = [2 ** i for i in range(len(self.successors))] 
        self.successors.sort(key=lambda x: min((x.position - (node_position + i)) % self.chord_size for i in i_values))

        print("remake routing table")
        for i in range(len(self.routing_table)):
            if self.routing_table[i].position == node_position:
                    self.routing_table[i] = self.lookup(self.routing_table[i].position + 1)

        j_values = [2 ** j for j in range(len(self.routing_table))]
        self.routing_table.sort(key=lambda x: min((x.position - (node_position + j)) % self.chord_size for j in j_values)) 


    def handle_post(self, data):
        data = request.get_data(as_text=True)
        name = self.ip
        print("url \' / \' invoked with data: " + name)
        file = open("/log/log.txt", 'a')
        file.write(name + "\n")

        return name

    def make_routing_table(self):
        table = []
        flag = False
        for i in range(len(self.routing_table)) :
            print("pos + " + str(2 ** i))
            result = self.lookup((2 ** i) + (self.position))
            print("result is" + str(result.position) + "\n\n\n")

            if result.position == self.position:
                flag = True
            if flag:
                table.append(table[-1])
            else:
                table.append(result)
            i = i + 1
        return table

    def is_alive(self, t: int):
        if self.active:
            if t == 1:
                print("check if sucessors are alive")
                for s in self.successors:
                    response = requests.post("http://" + s.ip)
                    if response.status_code != 200:
                        self.delete_node_from_routing(s.position)
                        print("node is unrechable")
                    else:
                        print("node ok")
                response = requests.post("http://" + self.predecessor.ip)
                if response.status_code != 200:
                    self.delete_node_from_routing(self.predecessor.position)
                    print("node is unrechable")
                else:
                    print("node ok")

            if t == 2:
                for r in self.routing_table:
                    response = requests.post("http://" + r.ip)
                    if response.status_code != 200:
                        self.delete_node_from_routing(r.position)
                        print("node is unrechable")
                    else:
                        print("node ok")

    def log(self):
        print("##################################################################")
        print("###################################################################")
        print("LOG")
        loger.log_routes(self)