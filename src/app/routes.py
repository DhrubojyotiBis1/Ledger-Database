from app import app, blockchain
from  flask import request

@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 400
    for node in nodes:
        blockchain.add_node(node)
        pass
    return {'nodes': nodes, 'added': True}, 201

@app.route('/nodes')
def nodes():
    serialised_nodes = []
    for node in blockchain.nodes:
        serialised_nodes.append(node)
    return {'nodes': serialised_nodes}