from flask import Flask
from app.block_chain import Blockchain
from pymongo import MongoClient

app = Flask(__name__)
blockchain = Blockchain()

cluster = MongoClient('mongodb+srv://Dhruv:raj1rick0@cluster0.z21gu.mongodb.net/<dbname>?retryWrites=true&w=majority')
db = cluster['testDatabase'] 
collection = db['testCollection']

from app import routes