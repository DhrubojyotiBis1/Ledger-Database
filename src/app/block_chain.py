import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse

class Blockchain():
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.transactions = []
        self.orphan_blocks = []
        self.create_block(proof = 1, previous_hash = '0')
    
    def create_block(self, proof, previous_hash, timestamp=str(datetime.datetime.now()), orphan_block_transaction=None):
        transactions = orphan_block_transaction if orphan_block_transaction else self.transactions
        block = {'index': len(self.chain) + 1,
                 'timestamp': timestamp,
                 'previous_hash': previous_hash,
                 'proof': proof,
                 'transactions': transactions,
        }
        if not orphan_block_transaction:
            self.transactions = []    
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while not check_proof:
            problem = new_proof**2 - previous_proof**2 #problem should not be symetric
            hash_operation = hashlib.sha256(str(problem).encode()).hexdigest() 
            if hash_operation[:4] ==  '0000':
                #more the number of leading zeros smaller the target and harder to get the proof of work 
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        previous_index = 1

        while previous_index < len(self.chain):
            #check if previous_hash is equal to previous block hash
            block = chain[previous_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            #check if hash_operation of previous_proof and current_proof is below the target
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            #update
            previous_block = block
            previous_index += 1
        
        return True
    
    def update_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.get_orphan_blocks(longest_chain)
            self.chain = longest_chain
            return True
        return False
    
    def is_valid_transaction(self, transaction):
        if type(transaction) is dict:
            insert = transaction['insert']
            where = transaction['where']
            if type(insert) is dict and type(where) is dict:
                if len(insert) >= 0 and len(where) >= 0:
                    return True
        return False

    def add_transaction(self, transaction):
        if self.is_valid_transaction(transaction):
            self.transactions.append(transaction)
            return True
        return False


    def commit_transaction(self, proof, previous_hash):
        #Update chain(if required) to get the longest chain
        self.update_chain()
        #create block and staged transaction to blockchain
        self.commit_orphan_block()
        self.create_block(proof, previous_hash)
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) 
    

    def get_orphan_blocks(self, longest_chain):
        thumb_rule = 0
        for self_block in reversed(self.chain):
            found = False
            for block in reversed(longest_chain):
                if self_block == block:
                    found = True
                    break
            thumb_rule += 1
            if not found and self_block['transactions']:
                self.orphan_blocks.append(self_block)
                thumb_rule = 0
            elif thumb_rule >= 6:
               break
    
    def commit_orphan_block(self):
        for block in self.orphan_blocks:
            transactions = block['transactions']
            timestamp = block['timestamp']
            if not transactions:
                pass
            previous_block = self.get_previous_block()
            previous_proof = previous_block['proof']
            proof = self.proof_of_work(previous_proof)
            previous_hash = self.hash(previous_block)
            commit_sucess = self.create_block(proof, previous_hash, timestamp, transactions)
        self.orphan_blocks = []