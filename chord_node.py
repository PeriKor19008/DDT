from datetime import datetime

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

    def log(self,mess:str):
        file = open("/log/log.txt", 'a')
        time = datetime.now()



        if "bootstrap" in mess:
            file.write(self.ip + "----" + mess + "-----" + time.strftime("%Y-%m-%d %H:%M:%S") + '\n'
                       + "-------" + "\n"
                       + "--------" + "\n"
                       + "success on join\n\n\n")
        else:
            file.write(self.ip + "----" + mess + "-----" + time.strftime("%Y-%m-%d %H:%M:%S") + '\n'
                       + "-------" + "\n"
                       + "--------" + "\n")

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

    def is_between(self,f:int,s:int,target:int):
        distance_clockwise = (target-f) % self.chord_size
        distance_counterclockwise = (s-target) % self.chord_size

        distance_f2s = (s-f) % self.chord_size

        return distance_clockwise < distance_f2s and distance_counterclockwise < distance_f2s



    def bootstrap(self,data):
        # get data
        host = data
        domain = "/insertnode"
        print("bbbbbbb")
        # send request
        response = requests.get(host + domain, json={"ip": self.ip})
        #self.log("bootstrap to "+data)
        data = response.content
        self.get_init_data(data)
        return data


    def handle_post(self,data):
        data = request.get_data(as_text=True)
        name = self.ip
        print("url \' / \' invoked with data: " + name)
        file = open("/log/log.txt", 'a')
        file.write(name + "\n")

        return name


    def init(self,data):


        new_node_ip = data["ip"]
        new_node_position = self.hash_ip(new_node_ip)

        new_node_successors = self.get_successors(new_node_position)
        new_node_predecessors = self.get_predecessor(new_node_position)

        json_successors=json.dumps(new_node_successors,default=Routes.serialize_routes,indent=2)
        json_predecessors = json.dumps(new_node_predecessors, default=Routes.serialize_routes, indent=2)
        data_to_send = {"position": new_node_position,
                        "successors": json_successors,
                        "predecessors": json_predecessors}

        data= json.dumps(data_to_send)
        #response = requests.post("http://"+new_node_ip + domain, json.dumps(data_to_send))
        #self.log("init " + new_node_ip)

        return data


    def get_init_data(self,data):
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

    def make_routing_table(self):
       return self.lookup(self.position+1)

    def lookup_iner(self,key:int):
        closest_successor = -1



        for pr in self.predecessors:
            if pr.position == key:
                return [pr, True]

        if self.routing_table != None:
            for r in self.routing_table:
                if r.position == key:
                    return [r, False]
                if r.position > closest_successor.position and r.position < key :
                    closest_successor = r

        f = self
        for suc in self.successors:

            if suc.position == key:
                return [suc,True]
            if self.is_between(f.position,suc.position,key):
                return [f,True]
            f = suc
            if closest_successor == -1:
                closest_successor=suc

            if (suc.position > closest_successor.position) and (suc.position < key) :
                closest_successor = suc



        return [closest_successor, False]

    def lookup(self,key:int):
        print(key)
        closest_successor = self.lookup_iner(key)
        if closest_successor[0]:
            return closest_successor[1]
        ip = "http://"+closest_successor.ip + "lookup"
        data_to_send = {"key":key}
        response = requests.post(ip,json={"key":key})
        #self.log("lookup")

        return response
    
    def is_alive(self):
        # Check if the next successor is alive
        next_successor_ip = self.lookup(self.position + 1).json()["ip"]
        next_successor_response = requests.post(f"http://{next_successor_ip}")
        if next_successor_response.status_code != 200:
            return "rebuild table"
        return "alive"

    def log_routes(self):
        file = open("/log/log"+self.ip.replace(".","_").replace(":","_").replace("/" , "_")+"_routes.txt", 'w')
        file.write("SUCCESSORS \n")
        for succ in self.successors:
            file.write("succ position: "+str(succ.position)+"---succ ip: "+succ.ip+"")
        file.write("SUCCESSORS \n------\n\n\nPREDECESSORS\n")
        for pre in self.predecessors:
            file.write("pre position: "+str(pre.position)+"---pre ip: "+pre.ip)
        file.write("PREDECESSORS\n-----\n\n\nROUTING TABLE\n")
        for route in self.routing_table:
            file.write("route position: "+str(route.position)+"---route ip: "+route.ip)

        return "routes"