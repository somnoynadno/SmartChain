import requests
import json
import hashlib

from urllib.parse import urlparse
from time import time

from models import SmartContract, SmartContractException, Port


class Blockchain:
    def __init__(self, port_id: str):
        self.current_transactions = []
        self.chain = []
        self.nodes = []
        self.port_id = port_id

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    @property
    def serialized_chain(self) -> []:
        sc = []
        for block in self.chain:
            new_block = {
                'index': block['index'],
                'timestamp': block['timestamp'],
                'transactions': [c.serialize() for c in block['transactions']],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
            }
            sc.append(new_block)

        return sc

    def execute_all(self):
        for block in self.chain:
            for contract in block['transactions']:
                try:
                    contract.execute(self.port_id)
                    print("ok")
                except SmartContractException as e:
                    print(e)

    def register_node(self, node: {}) -> bool:
        """
        Add a new node to the list of nodes
        """
        for n in self.nodes:
            if node['id'] == n.id:
                return False

        self.nodes.append(Port(node['id'], node['name'], node['address']))
        return True

    def valid_chain(self, chain) -> bool:
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'{node.address}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.nodes = [Port(n.id, n.name, n.address) for n in self.nodes]

            self.chain = []
            for block in new_chain:
                new_transactions = []
                for c in block['transactions']:
                    port_to = None
                    port_from = None
                    for node in self.nodes:
                        if node.id == c['to_address']:
                            port_to = node
                        if node.id == c['from_address']:
                            port_from = node

                    contract = SmartContract(port_from, port_to, c['cost'], c['uuid'], c['timestamp'], c['is_done'])
                    new_transactions.append(contract)

                new_block = block
                new_block['transactions'] = new_transactions
                self.chain.append(new_block)

            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        for elem in self.current_transactions:
            assert type(elem) == SmartContract

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, contract: SmartContract):
        """
        Creates a new transaction to go into the next mined Block

        """
        assert type(contract) == SmartContract
        self.current_transactions.append(contract)

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """
        sb = []
        for contract in block['transactions']:
            if type(contract) == SmartContract:
                sb.append(contract.serialize())
            else:
                sb.append(contract)

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(sb, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof

        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
