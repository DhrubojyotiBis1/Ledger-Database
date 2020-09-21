from app import app, blockchain, collection
from app.database import operate, drop_all_documents, select
from  flask import request
import requests
import socket

#BLOCKCHAIN API
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    node = request.args.get('node')
    if node is None:
        return 'No node', 400
    blockchain.add_node(node)   
    return node, 201

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return response

@app.route('/connect', methods=['GET'])
def connect():
    response_code = 400
    nodes = []
    existing_node_json = request.get_json()
    if existing_node_json:
        existing_node = existing_node_json.get('ex_node')
        self_node = f'{request.remote_addr}:5000'
        if existing_node and existing_node != self_node:
            url = f'{existing_node}/nodes'
            response = requests.get(url)
            existing_nodes = response.json()['nodes']
            existing_nodes.append(existing_node)
            for node in existing_nodes:
                if node != self_node:
                    url = f'{node}/connect_node?node=http://{self_node}'
                    response = requests.post(url)
                    if response.status_code == 201:
                        blockchain.add_node(node)
                        nodes.append(node)
            if len(blockchain.nodes):
                response_code = 201
    return {'nodes': nodes}, response_code


#USER API
@app.route('/nodes', methods = ['GET'])
def nodes():
    serialised_nodes = []
    for node in blockchain.nodes:
        serialised_nodes.append(node)
    return {'nodes': serialised_nodes}, 200

@app.route('/chain', methods = ['GET'])
def chain():
    blockchain.update_chain()
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return response, 200

@app.route('/transactions', methods = ['GET'])
def transactions():
    transactions = {'transactions': blockchain.transactions}
    return transactions, 200

@app.route('/add_transactions', methods=['POST'])
def add_transactions():
    if not blockchain.author_name:
        blockchain.author_name = request.remote_addr

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
    transactions = blockchain.transactions
    if not transactions:
        return 'Nothing to commit', 400
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    commit_sucess = blockchain.commit_transaction(proof, previous_hash)

    #insert in database
    for transaction in transactions:
        response_code = operate(transaction)
        if response_code != 200:
            return 'Something went wrong', response_code
    return 'Commited', 200

@app.route('/select', methods=['GET'])
def select_documents():
    json = request.get_json()
    commond = json.get('commond')
    if commond is None:
        return 'Bad commond', 400
    selected_documents, response_code = select(commond)
    if response_code == 400:
        return 'Wrong where commond', response_code
    return {'select': selected_documents}, response_code
    

@app.route('/drop_all', methods=['POST'])
def drop_all():
    #try to avoid this very, powerfull will delete every doc in collection
    #add somekind of authentication
    #add a block in blockchain with somekind of null pointer
    drop_all_documents()
    return 'dropped', 200
