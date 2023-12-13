
class Routes:
    def __init__(self, position:int, ip:str):
        self.position = position
        self.ip = ip

    def serialize_routes(obj):
        if isinstance(obj, Routes):
            return {'position': obj.position, 'ip': obj.ip}
        raise TypeError("Type not serializable")

    def deserialize_routes(routes):
        routes_list=[]
        for route in routes:
            routes_list.append(Routes(route['position'], route['ip']))
        #routes_list = [Routes(route['position'], route['ip']) for route in routes]
        return routes_list
