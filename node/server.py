import hashlib
import json
import os

from time import time
from uuid import uuid4

import requests

from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

from blockchain import Blockchain
from models import SmartContract


# Instantiate the Node
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Instantiate the Blockchain
blockchain = Blockchain(os.environ.get("PORT_ID"))
oracles = set()


@cross_origin()
@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # --> Reward for block mining is temporary removed <--

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    blockchain.execute_all()

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': [c.serialize() for c in block['transactions']],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@cross_origin()
@app.route('/contracts/new', methods=['POST'])
def new_contract():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['port_from', 'port_to', 'cost', 'uuid', 'timestamp']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Find related ports
    port_to = None
    port_from = None
    for node in blockchain.nodes:
        if node.id == values['port_to']:
            port_to = node
        if node.id == values['port_from']:
            port_from = node

    if not port_to or not port_from:
        return 'No such port', 400
    if port_to == port_from:
        return 'Ports matched', 400

    # Create a new SmartContract
    contract = SmartContract(port_from, port_to, values['cost'], values['uuid'], values['timestamp'])
    index = blockchain.new_transaction(contract)

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@cross_origin()
@app.route('/port', methods=['GET'])
def get_port():
    for node in blockchain.nodes:
        if node.id == blockchain.port_id:
            return node.serialize(), 200

    return {"status": "port not found"}, 500


@cross_origin()
@app.route('/contract/<id>/is_done', methods=['GET'])
def is_contract_done(id):
    if id in oracles:
        return {"status": "done"}, 200
    else:
        return {"status": "not done"}, 406


@cross_origin()
@app.route('/contract/<id>/export_oracle', methods=['POST'])
def export_oracle(id):
    oracles.add(id)
    return {"status": "OK"}, 200


@cross_origin()
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.serialized_chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@cross_origin()
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [n.serialize() for n in blockchain.nodes],
    }
    return jsonify(response), 201


@cross_origin()
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    blockchain.execute_all()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.serialized_chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.serialized_chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
