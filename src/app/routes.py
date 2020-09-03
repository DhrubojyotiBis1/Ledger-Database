from app import app, blockchain, collection
from app.database import operate
from  flask import request

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
    return {'nodes': nodes, 'added': True}, 201

@app.route('/nodes')
def nodes():
    serialised_nodes = []
    for node in blockchain.nodes:
        serialised_nodes.append(node)
    return {'nodes': serialised_nodes}

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return response

@app.route('/add_transactions', methods=['POST'])
def add_transactions():
    didAdd = False
    response_code = 400
    json = request.get_json()
    transactions = json.get('transactions')
    if transactions is None:
       return 'No transaction', response_code
    for transaction in transactions:
        didAdd = blockchain.add_transaction(transaction)
        if didAdd:
            response_code = 201
    return {'transactions': blockchain.transactions, 'added': didAdd}, response_code

@app.route('/commit', methods=['POST'])
def commit():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    transactions = blockchain.transactions
    commit_sucess = blockchain.commit_transaction(proof, previous_hash)

    #insert in database
    for transaction in transactions:
        operate(transaction)
    
    return 'Commited', 200
