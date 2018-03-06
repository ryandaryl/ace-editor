import os
from flask import Flask, send_from_directory, request, jsonify, Markup
from whitenoise import WhiteNoise
from rq import Queue
from worker import conn

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

@app.route('/')
def index():
    return send_from_directory(os.getcwd() + '/ace/public', 'index.html')

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