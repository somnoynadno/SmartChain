import requests

from uuid import uuid4
from time import time

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

ids = set()
nodes = []
contracts = []


@cross_origin()
@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    return jsonify(nodes), 200


@cross_origin()
@app.route('/get_contracts', methods=['GET'])
def get_contracts():
    return jsonify(contracts), 200


@cross_origin()
@app.route('/register_node', methods=['POST'])
def register_node():
    n = request.get_json()

    required = ['id', 'name', 'address']
    if not all(k in n for k in required):
        return 'Missing values', 400

    if n['id'] not in ids:
        nodes.append(n)
        ids.add(n['id'])

        for node in nodes:
            requests.post(f"{node['address']}/nodes/register", json={"nodes": nodes})
            requests.get(f"{node['address']}/nodes/resolve")

    return {"status": "OK"}, 200


@cross_origin()
@app.route('/create_contract', methods=['POST'])
def create_contract():
    c = request.get_json()
    c['uuid'] = str(uuid4())
    c['timestamp'] = int(time())

    required = ['port_from', 'port_to', 'cost']
    if not all(k in c for k in required):
        return 'Missing values', 400

    contracts.append(c)
    for node in nodes:
        requests.post(f"{node['address']}/contracts/new", json=c)

    return {"status": "OK"}, 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
