from app import collection

def operate(transaction):
    id = transaction['_id']
    if not transaction['removed'] :
        #ADDED
        document = transaction['added']
        document['_id'] = id
        collection.insert_one(document)
    elif not transaction['added'] :
        #DELETED
        document = transaction['removed']
        document['_id'] = id
        collection.delete_one(document)
    else:
        #MODIFIED
        collection.update_one({'_id': id}, {"$set": transaction['added']})