import os
from flask import Flask, send_from_directory, request, jsonify, Markup
from whitenoise import WhiteNoise
from rq import Queue
from worker import conn
import pymongo

app = Flask(__name__)

# Use this app to serve static files.
wnapp = WhiteNoise(app, root='./ace/public/')

q = Queue(connection=conn)

def get_status(job):
    status = {
        'id': job.id,
        'result': job.result,
        'status': 'failed' if job.is_failed else 'pending' if job.result == None else 'completed'
    }
    status.update(job.meta)
    return jsonify(status)

def exec_code(code):
    exec(code, globals())
    try:
        output = html_output
    except NameError:
        output = 'You can return html by defining a "html_output" variable.'
    return output

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

@app.route('/')
def index():
    return send_from_directory(os.getcwd() + '/ace/public', 'index.html')

@app.route("/save", methods=['GET', 'POST'])
def save():
    print(request.values)
    save_to_mongo(request.values.get('code'))
    return jsonify({'message': 'Saved {} characters to MongoDB Cloud.'.format(len(load_from_mongo()))})

@app.route("/load")
def load():
    return jsonify({'code': load_from_mongo()})

@app.route("/run", methods=['GET', 'POST'])
def handle_code():
    query_id = request.values.get('job')
    if query_id:
        found_job = q.fetch_job(query_id)
        if found_job:
            if found_job.result:
                output = found_job.result
            else:
                output = get_status(found_job)
        else:
            output = jsonify({ 'id': None, 'error_message': 'No job exists with the id number ' + query_id })
    else:
        code = request.values.get('code')
        new_job = q.enqueue(exec_code, code, timeout='1h')
        output = get_status(new_job)
    return output