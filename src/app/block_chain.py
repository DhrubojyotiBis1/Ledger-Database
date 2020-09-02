import datetime
import hashlib
from urllib.parse import urlparse
import json

class Blockchain():
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.create_block(proof = 1, previous_hash = '0')
    
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'previous_hash': previous_hash,
                 'proof': proof
        }     
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
    
    def is_valid_chain(self, chain):
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
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) 
    
