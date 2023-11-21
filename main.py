from CHORD import Chord_node
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_post():
    data = request.get_data(as_text=True)
    return data

@app.route('/init', methods=['POST'])
def handle_post_init():
    data = request.get_data(as_text=True)
    return data+"init"

if __name__ == '__main__':
    node = Chord_node.node_init()
    print("node ready")
    app.run(host='0.0.0.0', port=5000)





