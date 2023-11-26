from CHORD_test import Chord_node
from flask import Flask, request
import requests

app = Flask(__name__)



if __name__ == '__main__':
    host = 'http://172.19.0.3:5000/'
    response = requests.post(host, "peri init")
    print(response)





