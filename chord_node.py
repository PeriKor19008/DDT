from B_tree import BTree
from flask import Flask, request, make_response
import requests
import json
import socket
from routes import Routes
from typing import List
import math


class ChordNode:

    def __init__(self,size):

        self.chord_size=size
        self.successor_num = int(math.log2(self.chord_size))
        self.ip = self.get_ip()
        temp_self_route = Routes(-1,self.ip)
        self.predecessors: List[Routes] = [temp_self_route]
        self.successors: List[Routes] = [temp_self_route]
        self.routing_table: List[Routes] = None
        self.btree: BTree
        self.position:int


    def get_successors(self,position):
        suc_list = []
        if self.successors[0].ip==self.ip:
            self.position=self.hash_ip(self.ip)
            tmp = self.successors[0]
            tmp.position=self.position
            suc_list.append(tmp)
            return suc_list
        for suc in range(position + self.successor_num):
            suc_list.append(self.lookup(suc))
        return suc_list

    def get_predecessor(self,position):
        pre_list = []
        if self.successors[0].ip==self.ip:
            self.position = self.hash_ip(self.ip)
            tmp = self.successors[0]
            tmp.position = self.position
            pre_list.append(tmp)
            return pre_list
        for pre in range(position + self.successor_num):
            pre_list.append(self.lookup(pre))
        return pre_list

    def get_ip(self):
        name = socket.gethostname()
        return socket.gethostbyname(name) + ":5000/"

    def hash_ip(self,ip: str):
        hash = 0
        for i in ip:
            hash = ord(i) * 7 + hash
        return hash % self.chord_size



    def bootstrap(self,data):
        # get data
        host = data
        domain = "/insertnode"
        print("bbbbbbb")
        # send request
        response = requests.post(host + domain, json={"ip": self.ip})
        return data


    def handle_post(self,data):
        data = request.get_data(as_text=True)
        name = self.ip
        print("url \' / \' invoked with data: " + name)
        return name


    def init(self,data):


        new_node_ip = data
        new_node_position = self.hash_ip(new_node_ip)

        new_node_successors = self.get_successors(new_node_position)
        new_node_predecessors = self.get_predecessor(new_node_position)

        json_successors=json.dumps(new_node_successors,default=Routes.serialize_routes,indent=2)
        json_predecessors = json.dumps(new_node_predecessors, default=Routes.serialize_routes, indent=2)
        data_to_send = {"position": new_node_position,
                        "successors": json_successors,
                        "predecessors": json_predecessors}

        domain = "/init_data"
        dt = json.dumps(data_to_send)
        response = requests.post(new_node_ip + domain, json.dumps(data_to_send))

        return data


    def get_init_data(self,data):

        data = json.loads(data)

        tmp = json.loads(data["successors"])
        self.successors = Routes.deserialize_routes(tmp)
        tmp = json.loads(data["predecessors"])
        self.predecessors = Routes.deserialize_routes(tmp)
        self.position = data.get("position")

        self.routing_table = self.make_routing_table()

    def make_routing_table(self):
        return -1

    def lookup_iner(self,key:int):
        closest_successor = -1
        for pr in self.predecessors:
            if pr.position == key: return pr

        for suc in self.successors:
            if suc.position == key: return suc

            if (suc.position > closest_successor.position) and (suc.position < key):
                closest_successor = suc

        if self.routing_table != None:
            for r in self.routing_table:
                if r.position == key: return r
                if r.position > closest_successor.position and r.position < key :
                    closest_successor = r

        return closest_successor

    def lookup(self,key:int):
        closest_successor = self.lookup_iner(key)
        if closest_successor.position == key: return closest_successor
        ip = closest_successor.ip + "/lookup"
        data_to_send = {"key":key}
        response = requests.post(ip,json.dumps(data_to_send))
        return response
    
    def is_alive(self):
        # Check if the next successor is alive
        next_successor_ip = self.lookup(self.position + 1).json()["ip"]
        next_successor_response = requests.post(f"http://{next_successor_ip}")
        if next_successor_response.status_code != 200:
            return "rebuild table"
        return "alive"