import socket
from chord_node_log import ChordNodeLog

loger = ChordNodeLog()
class ChordNodeHelper:


    def __init__(self):
        self.collision_counter: int = 0


    def is_between(self,f:int,s:int,target:int,chord_size:int) -> bool:
        distance_clockwise = (target-f) % chord_size
        distance_counterclockwise = (s-target) % chord_size

        distance_f2s = (s-f) % chord_size

        return distance_clockwise < distance_f2s and distance_counterclockwise < distance_f2s


    # Added argument "collision",default: False, for re-calculating position
    def hash(self, string: str, chord_size: int, collision=False) -> int:
        h = 0
        for i in string:
            h = ord(i) * 7 + h
        result = h % chord_size
        print("----------------------------------------------"
              + "\nHASH\n"
              + "string:" + str(string) + "  result:" + str(result))
        
        # If the hash is called with true statement then change the hashing
        # Not sure if its correct to multiply by 11
        # Tested adding 11 and gave position 5960
        if collision:
            new_position = h*(11 + self.collision_counter)  % chord_size
            self.collision_counter += 1
            return new_position
        
        self.collision_counter = 0

        return h % chord_size


    def get_ip(self) -> str:
        name = socket.gethostname()
        return socket.gethostbyname(name) + ":5000/"