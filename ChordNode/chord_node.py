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

        self.make_routing_table()

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
        loger.log_routes(self)

        #if chord empy or if key belongs to node
        if self.successors[0].position == self.position or helper.is_between(self.predecessor.position, self.position + 1, key, self.chord_size):
            print("returning self route because chrod is empty")
            return Routes(self.position, self.ip)

        #if routing table empty
        if self.routing_table[0].position == self.position:
            print("returning successor because routing table is empty")
            return self.successors[0]

        closest_route = self.successors[0]

        for route in self.routing_table:
            if route.position == self.position or route.position == closest_route.position:
                break
            if helper.is_between((closest_route.position - 1) % self.chord_size, route.position, key, self.chord_size):
                break
            closest_route = route
            if closest_route.position == self.position:
                print("returning self route because closest route is self")
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


    def depart(self):
        requests.post("http://" + self.predecessor.ip + "/suc_depart", json={"suc_num":1})
        self.active = False


    def successor_depart(self,suc_num: int):
        if suc_num == 1:
            requests.post("http://" + self.predecessor.ip + "/suc_depart", json={"suc_num": 2})
            self.successors[0]=self.successors[1]
            self.successors[1] = self.lookup((self.successors[1].position + 1) % self.chord_size)
            requests.post("http://" + self.successors[0].ip + "/pred_depart",json={"ip": self.ip, "pos": self.position})
        else:
            self.successors[1] = self.lookup((self.successors[1].position + 1) % self.chord_size)


    def predecessor_depart(self,data):
        self.predecessor = Routes(data["pos"], data["ip"])


    def insert_data(self, data):

        if isinstance(data, bytes):
            decoded_data = json.loads(data.decode('utf-8'))
            data = decoded_data.get("keys", [])

        for item in data:
            key = helper.hash(item['Education'], self.chord_size)

            target_node = self.lookup(key)
            print(target_node.ip)
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
        if tree_data:
            self.btree.insert(tree_data)
            if send_to_suc:
                print("sending to successors")
                print(tree_data)
                self.btree.owned(tree_data["Education"])
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
        print(f"This is the search key: {search_key}")
        print(f"This is the target ip: {target_node.ip}")
        
        if target_node.ip == self.ip:

            matches = self.btree.search(search_key)
            print(matches)
            if not matches:
                return "\n\n No matches \n\n"
            else:
                return jsonify(matches)
        else:
            target_node_ip = "http://" + target_node.ip + "/retrieve_data"
            response = requests.get(target_node_ip, json={"Education": search_key})

            return response.text


    def make_routing_table(self):
        self.routing_table[0] = self.successors[0]
        flag = False
        print("\n\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
              "MAKE ROUTING TABLe")
        for i in range(1,len(self.routing_table)) :
            print("pos + " + str(2 ** i))
            result = self.lookup(((2 ** i) + (self.position)) % self.chord_size)
            print("result is" + str(result.position) + "\n\n\n")

            if result.position == self.position:
                flag = True
                print("Flag = TRUE")
            if flag:
                print("table apending last element:" + str(self.routing_table[-1].position))
                self.routing_table[i] = self.routing_table[-1]
            else:
                print("table apending result:" + str(result.position))
                self.routing_table[i] = result
        print("\n\n\n\n\n\n")


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
                            s = Routes(self.successors[i].position, self.successors[i].ip)

                        else:
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
                    while True:
                        response = requests.get("http://" + r.ip + "/get_predecessor")
                        if response.status_code == 200:
                            data = response.json()
                            print("Correct Curl ")
                            print("for node:" + str(self.position)
                                  + "route num:" + str(i) + "position is: " + str(r.position)
                                  + " \nideal pos" + str((2**i + self.position) % self.chord_size)  + " response pos:" + str(data["pos"]))
                            if helper.is_between((self.position + 2**i) % self.chord_size -1, r.position, int(data["pos"]), self.chord_size):

                                self.routing_table[i] = Routes(data["pos"], data["ip"])
                            break
                        else:
                            self.routing_table[i] = self.lookup(self.routing_table[i].position + 1)
                            r = self.routing_table[i]


    def log(self):
        print("##################################################################")
        print("###################################################################")
        print("LOG")
        loger.log_routes(self)
