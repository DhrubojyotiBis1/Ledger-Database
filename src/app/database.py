from app import collection

def operate(commond):
    response_code = 500
    for key in commond.keys():
        if key != 'insert' or key != 'where':
            return 400
    if commond['insert'] and not commond['where']:
        #INSERTED
        document = commond['insert']
        document['_id'] = get_id()
        try:
            inserted_document = collection.insert_one(document)
            response_code = 200
        except:
            response_code = 409
    elif commond['where'] and not commond['insert']:
        #DELETED
        deleted_documents = collection.delete_many(commond['where'])
        response_code = 404 if deleted_documents.deleted_count == 0 else 200
    else:
        #MODIFIED
        modified_documents = collection.update_many(commond['where'], {"$set": commond['insert']})
        response_code = 400 if modified_documents.modified_count == 0 else 200
    return response_code

def select(commond):
    #SELECT
    response_document_list = [] 
    key = list(commond.keys())[0]
    if key == 'where':
        selected_documents = collection.find(commond['where']) 
        for document in selected_documents:
            response_document_list.append(document)
        return response_document_list, 200
    return response_document_list, 400

    
def drop_all_documents():
    collection.delete_many({})

def get_id():
    return collection.count() + 1