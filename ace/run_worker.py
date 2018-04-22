import json
from rq import Queue
from worker import conn

q = Queue(connection=conn)

def get_status(job):
    status = {
        'id': job.id,
        'result': job.result,
        'status': 'failed' if job.is_failed else 'pending' if job.result == None else 'completed'
    }
    status.update(job.meta)
    return json.dumps(status)

def exec_code(code):
    exec(code, globals())
    try:
        output = html_output
    except NameError:
        output = 'You can return html by defining a "html_output" variable.'
    return output

def run(data_json):
    query_id = data_json.get('job')
    if query_id:
        found_job = q.fetch_job(query_id)
        if found_job:
            if found_job.result:
                output = found_job.result
            else:
                output = get_status(found_job)
        else:
            output = json.dumps({ 'id': None, 'error_message': 'No job exists with the id number ' + query_id })
    else:
        code = data_json.get('code')
        new_job = q.enqueue(exec_code, code, timeout='1h')
        output = get_status(new_job)
    return output