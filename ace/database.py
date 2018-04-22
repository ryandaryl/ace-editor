import pymongo

def mongo_connect():
    url = 'mongodb://genincweather:INFO30005@weather-shard-00-00-hifln.mongodb.net:27017,weather-shard-00-01-hifln.mongodb.net:27017,weather-shard-00-02-hifln.mongodb.net:27017/<DATABASE>?ssl=true&replicaSet=weather-shard-0&authSource=admin'
    client = pymongo.MongoClient(url)
    return client.test_db

def load_from_mongo():
    db = mongo_connect()
    post_list = []
    for post in db.ace_col.find():
        post_list.append(post)
    return post_list[0]['code']

def save_to_mongo(code):
    db = mongo_connect()
    db.ace_col.delete_many({})
    db.ace_col.insert_one({'code': code})