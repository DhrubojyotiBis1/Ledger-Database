from flask import Flask
from app.block_chain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

from app import routes