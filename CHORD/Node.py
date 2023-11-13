from BTree import BTree
class Node:
    ip:str
    data:BTree
    successors=[]
    routingTable=[]

    def bootstap(self):
        # function to "join" node to chord
        return -1

    def  hash_function_node(self,ip):
        # hash func for node ip
        return -1


    def hash_function_key(self):
        # hash func for key
        return -1

    def key_lookup(self,key):
        # find node that has or will save the key
        self.hash_function_key()
        #lookup node that hash func returns

    def insert_data(self,key):
        # insert data to appropriate node
        self.key_lookup(key)
        #inset data to node returned

    def retrieve_data(self, key):
        # retrieve data from node that stores it
        self.key_lookup(key)
        #retrive data from node returned

    def store_data(self,key):
        # store data in local BTree
        # back up data to appropriate node
        return -1

    def get_stored_data(self,key):
        # return data stored in local BTree
        return -1

    def successors_maintance(self):
        # periodically run or provoked adhoc
        # update the successors list
        return -1

    def update_routing_table(self):
        # update the routing table
        return -1

    def insert_new_node(self,ip):
        # insert new node to chord based on ip

        # insert node base on hashed ip
        self.hash_function_node()

        #if needed update routing table or successors list

    def depart_chord(self):
        # controlled departure from chord
        return -1

