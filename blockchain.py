import hashlib
import json
import sys
import requests

from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()

        # The genesis block
        self.new_block(previous_hash = 1, proof = 100)

    def new_block(self, proof, previous_hash = None):
        """
        Creates a new block in the blockchain

        :param proof: <int>
        :param previous_hash: <string>
        :return:
        """

        newBlock = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # reset the current list of transactions
        self.transactions = []

        self.chain.append(newBlock)
        return newBlock

    def new_transaction(self, sender, recipient, amount):
        """
        Adds a new transaction to the list of transactions

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> The amount of the transaction
        :return: <int> the index of the block that will hold this transaction
        """

        self.transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last):
        """
        Proof of work algorithm
        :param last: <hash> the previous hash from the previous block
        """

        proof = 0
        while self.valid_proof(last, proof) is False:
            proof += 1

        return proof

    def register_node(self, address):
        """
        Adds a new address to the current list of registered addresses
        :param address: <str> The address to be added to the adjacent node list
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        determines if a given chain is valid
        :param chain: <list> the chain to be validated
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('\n------------\n')

            # check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                print("The previous hash was NOT the previous!!!")
                return False

            # check that the proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                print("Not a valid hash!!!")
                return False

            last_block = block 
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        The consensus algorithm
        """

        neighbors = self.nodes
        new_chain = None 

        max_length = len(self.chain)

        for node in neighbors: 
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # check if the length is longer than this nodes chain
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain 

        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def valid_proof(last, proof):
        """ 
        Validates the previous proof
        :param proof: <int> The proof of work
        """

        guess = f'{last}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        # print(guess_hash)
        
        # This is where we test the hash against the "hardness"
        return guess_hash[:1] == "0"

    @staticmethod
    def hash(block):
        """
        Hashes a block's information
        :param block: <Block> The block to be hashed
        """
    
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        Returns the last block in the chain
        """
        
        return self.chain[-1]


"""
----------
Set up the Flask app
----------
"""
app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

"""
----------
Flask app routes
----------
"""

@app.route('/mine', methods=['GET'])
def mine():
    # Mine a new block
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Send the reward!
    blockchain.new_transaction(
        sender = '0',
        recipient = node_identifier,
        amount = 1
    )

    # Forget the new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block added to chain!",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods = ['POST'])
def new_transaction():
    # Add a new transaction to the trans list

    values = request.get_json()

    # check that the required fields are in the posted data
    required = ['sender', 'recipient', 'amount']
    if not all(i in values for i in required):
        return 'Invalid JSON! Missing keys', 400

    # generate a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transactions will be added to block {index}'}
    return jsonify(response), 200

@app.route('/chain', methods = ['GET'])
def get_chain():
    # Returns the full chain to the end user
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/nodes/register', methods =['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 200


@app.route('/nodes/resolve', methods = ['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain 
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = int(sys.argv[1]))