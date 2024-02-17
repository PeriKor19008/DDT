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
        self.successors: List[Routes] = [temp_self_route] * 2
        self.routing_table: List[Routes] = [temp_self_route] * int(math.log2(self.chord_size))
        self.predecessor: Routes = temp_self_route
        self.btree: BTree = BTree(False)
        print("ip:" + str(self.ip)
              + "\nposition:" + str(self.position)
              + "\n")


    def bootstrap(self, data):

        print("\n\n\n\######## bootstrap of " + str(self.position) + " ##########\n\n\n")
        self.active = True
        host = data
        domain = "/get_succ"

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
        data = json.loads(data)
        tmp = json.loads(data["successor"])
        self.successors[0] = Routes(tmp['position'], tmp['ip'])
        tmp =self.lookup(self.successors[0].position + 1)
        if tmp.position == self.position:
            self.successors[1] = self.successors[0]
        else:
            self.successors[1] = tmp
        if self.successors[0].position == self.successors[1].position:
            self.predecessor = self.successors[0]
        response = requests.get("http://" + self.successors[0].ip + "/new_predecessor", json={"ip": self.ip, "pos": self.position})


        #### EFREM use response to save your keys
        info = response.json()
        for keys in info:
            self.btree.insert(keys)
            self.btree.backup_data.add(keys["Education"])


        self.routing_table = self.make_routing_table()
        self.stabilize()
        loger.log_routes(self)

        print("\n\n\n\n\n\n.")
        return data

    def set_pred(self,data):
        print("SET PRED for" + str(self.position) +" with data:" +str(data["pos"]))
        self.predecessor = Routes(data["pos"] , data["ip"])

    def new_predecessor(self,data):
        new_pred_ip = data["ip"]
        new_pred_pos = data["pos"]

        print("\n\n\n\######## new_predecessor by: " + str(self.position) + "||invoked from: " + str(new_pred_pos))


        old_pred_ip = self.predecessor.ip
        old_pred_pos = self.predecessor.position
        self.predecessor = Routes(new_pred_pos, new_pred_ip)

        # if first on chord
        if old_pred_pos != self.position:
            print("\n\n\n######## new_successor NOT first by:" + str(old_pred_pos) + "invoked from: " +str(self.position) + " with data: " +str(self.predecessor.position))

            requests.post("http://" + old_pred_ip + "/new_successor", json={"ip": self.predecessor.ip,
                                                                "pos": self.predecessor.position})
        else:
            self.successors[0] = self.predecessor
            self.successors[1] = self.predecessor
            print("\n\n\n######## new_successor FIRST by:" + str(self.successors[0].position) + "invoked from: " + str(
                self.position) + " with data: " + str(self.position))

            requests.post("http://" + self.successors[0].ip + "/new_successor", json={"ip": self.ip,
                                                                            "pos": self.position})
            for r in range(len(self.routing_table)):
                self.routing_table[r] = self.successors[0]

        keys_to_send = []
        for key in self.btree.owned_data:
            if helper.is_between(old_pred_pos, self.predecessor.position + 1, key, self.chord_size):
                keys_to_send.append(key)
                self.btree.owned_data.remove(key)

        json_data = []
        for send_keys in keys_to_send:
            json_data.append(self.search_data(send_keys))

        ## EFREM delete back keys of old pred (btree.backup_data)
        for backup_keys in self.btree.backup_data:
            self.btree.delete(backup_keys)
            self.btree.backup_data.remove(backup_keys)




        for key in keys_to_send:
            self.btree.backup_data.add(key)

        self.stabilize()
        ## send keys to
        return json_data

    def new_successor(self,data):
        new_suc_ip = data["ip"]
        new_suc_pos = data["pos"]

        if new_suc_pos == self.position:
            return "success"

        self.successors[1] = self.successors[0]
        tmp = Routes(new_suc_pos,new_suc_ip)
        if tmp.position == self.position:
            self.successors[1] = self.successors[0]
        else:
            self.successors[0] = tmp


        if self.routing_table[0].position == self.position:
            for i in range(len(self.routing_table)):
                self.routing_table[i] = self.successors[0]

        ## copy keys to new succ
        send_keys = []
        for keys in self.btree.owned_data:
            send_keys.append(self.search_data(keys))
        if send_keys:
            requests.post("http://" + self.successors[0].ip + "/backup_data", json=send_keys)

        print("\n\n\n\n\n#########################3")
        response = requests.post("http://" +self.successors[0].ip + "/pred_notif", json={"ip": self.ip, "pos": self.position})
        self.stabilize()
        return "success"


    def get_succ(self, data):
        self.active = True
        new_node_ip = data["ip"]
        new_node_position = data["pos"]
        print("\n\n\n\######## get_succ by: " + str(self.position) + "||invoked from: " + str(new_node_position))
        
        # Checks if position already exists
        # Returns json with key:error
        collision_node = self.lookup(new_node_position)
        if collision_node.position == new_node_position:
            return {"error":"position"}

        
        new_node_successor = self.lookup(new_node_position + 1)


        json_successors = json.dumps(new_node_successor, default=Routes.serialize_routes, indent=2)
        data_to_send = {"successor": json_successors}
        data = json.dumps(data_to_send)
        return data


    def lookup(self, key: int):

        key = key % self.chord_size  # to be sure that the key is inside the chord bounds
        print("\n\n\n\######## lookup key:" + str(key) + " by node with  pos:" + str(self.position))
        #loger.log_routes(self)

        #if chord empy or if key belongs to node
        if self.successors[0].position == self.position or helper.is_between(self.predecessor.position, self.position + 1, key, self.chord_size):
            return Routes(self.position, self.ip)

        #if routing table empty
        if self.routing_table[0] == self.ip:
            return self.successors[0]

        closest_route = self.successors[0]

        for route in self.routing_table:
            if route.position == self.position or route.position == closest_route.position:
                break
            if helper.is_between((closest_route.position - 1) % self.chord_size, route.position, key, self.chord_size):
                break
            closest_route = route
            if closest_route.position == self.position:
                return Routes(self.position, self.ip)

        response = requests.get("http://" + closest_route.ip + "lookup", json={"key": key})
        if response.status_code != 200:
            if closest_route.position == self.successors[0].position:
                self.stabilize(1)
                return self.lookup(key)
            else:
                response = requests.get("http://" +self.successors[0].ip + "lookup", json={"key": key})
        data = json.loads(response.content.decode('utf-8'))
        return Routes(data["position"], data["ip"])



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
        if len(tree_data) > 0:
            self.btree.insert(tree_data)
            if send_to_suc:
                keys = tree_data.get("Education", [])
                self.btree.owned(keys)
                result = self.backup_data(tree_data)
                return result
            return "Data stored"
        else:
            return "No data to store"
        
    def backup_data(self, tree_data):

        target_node_ip = "http://" + self.successors[0].ip + "/backup_data"
        requests.post(target_node_ip, json=tree_data,
                      headers={'Content-Type': 'application/json'})


        return "Data sent to Successors"

    def retrieve_data(self, search_key):

        # for data in search_key:
        target_node = self.lookup(helper.hash(search_key, self.chord_size))

        if target_node.ip == self.ip:
            if not hasattr(self, 'btree'):
                return "B-tree is not initialized"

            matches = self.btree.search(search_key)
            if len(matches) == 0:
                print("\n\n No matches \n\n")
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

            # if response.status_code != 200:
            #     result = self.lookup(target_node.position + 1)
            #     result_ip = "http://" + result.ip + "/search_data"
            #     response = requests.get(result_ip, json={"Education": search_key})

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
            if tmp:
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
                        break
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


            for i in range(len(self.routing_table)):

                print("\n\n\n\n#######################\ninform for routes "
                      "self pos:" + str(self.position) + "ideal pos:"
                      + str(self.position + (2 ** i) + 1) + "node pos:" + str(node_position))
                if i == 0:
                    self.routing_table[0] = self.successors[0]
                    continue
                if helper.is_between((self.position + (2 ** i) ) % self.chord_size,self.routing_table[i].position, node_position, self.chord_size):
                    print("route inserted")
                    self.routing_table[i] = Routes(node_position, node_ip)
                    print("route inserted" + str(self.routing_table[i].position))
                print("\n\n\n")
                f = self.position + (2 ** i)

                # if self.position == self.routing_table[i].position or (helper.is_between( self.position+(2 ^ i), self.routing_table[i].position, node_position, self.chord_size)):
                #     tmp = Routes(node_position, node_ip )
                #     self.routing_table[i] = tmp
                #     print("geting node" + str(node_position) + " in routing table place:" + str(i))


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
        file = open("/log/log.txt", 'a')
        file.write(name + "\n")

        return name

    def make_routing_table(self):
        table = []
        table.append(self.successors[0])
        flag = False
        for i in range(1,len(self.routing_table)) :
            print("pos + " + str(2 ** i))
            result = self.lookup(((2 ** i) + (self.position)) % self.chord_size)
            print("result is" + str(result.position) + "\n\n\n")

            if result.position == self.position:
                flag = True
            if flag:
                table.append(table[-1])
            else:
                table.append(result)

        return table

    def stabilize(self, t: int = 0):
        if self.active:
            if t == 1 or t == 0:
                pos = self.position
                for i in range(len(self.successors)):

                    s = Routes(self.successors[i].position, self.successors[i].ip)
                    while True:
                        response = requests.get("http://" + s.ip + "/get_predecessor")

                        if response.status_code != 200:
                            if i == 0:
                                print("a")
                                self.successors[0] = self.successors[1]
                                self.successors[1] = self.lookup(self.successors[0].position + 1)

                            else:
                                print("b")
                                self.successors[1] = self.lookup(self.successors[0].position + 1)


                        data = response.json()
                        print("\n\nresponse for stabilaze of node " + str(pos) + "is: " + str(data["pos"]) + "on suc num: " + str(i))
                        if i==0 or (self.successors[0].position != self.predecessor.position and i>0):
                            print("not first in network")
                            if data["pos"] != pos:
                                s = Routes(data["pos"],data["ip"])
                                print("c " +str(data["pos"]))

                            else:
                                self.successors[i] = Routes(s.position, s.ip)
                                flag = False
                                break
                        else:
                            print("First on network")
                            self.successors[0] = self.successors[1]
                            break
                    pos = self.successors[i].position

            if t == 2 or t == 0:
                for i in range(len(self.routing_table)):
                    r = self.routing_table[i]
                    response = requests.get("http://" + r.ip + "/get_predecessor")
                    data = response.json()
                    if helper.is_between(self.position + 2**i,r.position,int(data["pos"]),self.chord_size):
                        self.routing_table[i] = Routes(data["pos"], data["ip"])

    def log(self):
        print("##################################################################")
        print("###################################################################")
        print("LOG")
        loger.log_routes(self)









    # def get_init_data(self, data):
    #     print(data)
    #     data = json.loads(data)
    #
    #     tmp = json.loads(data["successors"])
    #     self.successors = Routes.deserialize_routes(tmp)
    #     tmp = json.loads(data["predecessor"])
    #     self.predecessor = Routes(tmp['position'], tmp['ip'])
    #
    #     for i in range(len(self.routing_table)):
    #         self.routing_table[i] = self.successors[0]
    #     print("log1")
    #     loger.log_routes(self)
    #     print("log2")
    #     self.routing_table = self.make_routing_table()
    #
    #     return "self.routing_table"
