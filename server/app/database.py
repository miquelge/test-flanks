import pymongo

class DB(object):

    URI = "mongodb://127.0.0.1:27017"

    @staticmethod
    def init():
        client = pymongo.MongoClient(DB.URI)
        DB.DATABASE = client['flanks_test']

    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return DB.DATABASE[collection].find(query, {'_id': False})

    @staticmethod
    def remove(collection, query):
        return DB.DATABASE[collection].remove(query)
