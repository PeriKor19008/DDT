from B_tree import BTree
from flask import Flask, request, make_response
import requests
import json
import socket


class ChordNode:

    def __init__(self):

        self.chord_size:str
        self.ip = self.get_ip()
        self.successor = [self]
        self.predecessor = [self]
        self.routing_table = []
        self.btree: BTree
        self.position:int


    def get_successors(self,position):
        return -1

    def get_predecessor(self,position):
        return -1

    def get_ip(self):
        name = socket.gethostname()
        return socket.gethostbyname(name) + "/5000"

    def hash_ip(self,ip: str):
        hash = 0
        for i in ip:
            hash = int(i) * 7 + hash
        return hash % 32

 #test

    def bootstrap(self,data):
        # get data
        data = json.loads(request.get_data(as_text=True))
        host = data("ip")
        domain = "insertnode"
        # send request
        response = requests.post(host + domain, json={"ip": self.ip})
        return data


    def handle_post(self,data):
        data = request.get_data(as_text=True)
        name = self.ip
        print("url \' / \' invoked with data: " + name)
        return name


    def init(self,data):
        data = json.loads(request.get_data(as_text=True))

        new_node_ip = data("ip")
        new_node_position = self.hash_ip(new_node_ip)

        new_node_successors = self.get_successors(new_node_position)
        new_node_predecessors = self.get_predecessor(new_node_position)

        data_to_send = {"position": new_node_position,
                        "successors": new_node_successors,
                        "predecessors": new_node_predecessors}

        domain = "inti_data"
        response = requests.post(new_node_ip + domain, json.dumps(data_to_send))

        return data


    def get_init_data(self,data):
        data = json.loads(request.get_data(as_text=True))
        self.position = data("position")
        self.successor = data("successors")
        self.predecessor = data("predecessors")
        self.routing_table = self.make_routing_table

    def make_routing_table(self):
        return -1