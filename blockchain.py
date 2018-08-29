import hashlib
import json
from time import time

class Blockchain(obj):
    def __init__(self):
        self.chain = []
        self.transactions = []

        # The genesis block
        self.new_block(previous_hash = 1, proof = 100)

    def new_block(self):
        # Creates a new block and adds it to the blockchain

        pass

    def new_transaction(self, sender, recipient, amount):
        """
        Adds a new transaction to the list of transactions

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> The amount of the transaction
        :return: <int> the index of the block that will hold this transaction
        """

        self.transaction.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # hashes a block's information
        pass

    @property
    def last_block(self):
        # returns the last block in the chain
        pass

    