import os

import pymongo as pm
from bson.objectid import ObjectId

LOCAL = "0"
CLOUD = "1"

DB_NAME = 'SWE_DESIGN_PROJECT'

client = None

MONGO_ID = '_id'


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print("Setting client because it is None.")
        if os.environ.get("CLOUD_MONGO", LOCAL) == CLOUD:
            password = os.environ.get("MONGO_PASSWORD")
            username = os.environ.get("MONGO_USERNAME")
            if not password:
                raise ValueError('You must set your password '
                                 + 'to use Mongo in the cloud.')
            url = f"mongodb+srv://{username}:{password}@cluster0.\
mpx0yi5.mongodb.net/?retryWrites=true&w=majority"
            print(url)
            print("Connecting to Mongo in the cloud.")
            client = pm.MongoClient(url.format(password, username))
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient()


def insert_one(collection, doc, db=DB_NAME):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return client[db][collection].insert_one(doc)


def fetch_one(collection, filt, db=DB_NAME):
    """
    Find with a filter and return on the first doc found.
    """
    for doc in client[db][collection].find(filt):
        if MONGO_ID in doc:
            # Convert mongo ID to a string so it works as JSON
            doc[MONGO_ID] = str(doc[MONGO_ID])
        return doc


def del_one(collection, filt, db=DB_NAME):
    """
    Find with a filter and return on the first doc found.
    """
    client[db][collection].delete_one(filt)


def fetch_all(collection, db=DB_NAME):
    ret = []
    for doc in client[db][collection].find():
        ret.append(doc)
    return ret


def fetch_all_as_dict(key, collection, db=DB_NAME):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret


def find_by_id(id, collection, db=DB_NAME):
    return client[db][collection].find({'_id': ObjectId(id)})


def exists_by_id(id, collection, db=DB_NAME):
    return client[db][collection].count_documents({'_id': ObjectId(id)}) != 0


if __name__ == "__main__":
    test = connect_db()
    cur = find_by_id("6557c2c7328bd0df911c9ec6", "users")
    print(exists_by_id("6557c2c7328bd0df911c9ec7", "users"))
    print(os.environ.get("DB_NAME", LOCAL))
    for i in cur:
        print(i)
