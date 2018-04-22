import json
from tornado import websocket, web, escape
from tornroutes import route
import ace.database as database
import ace.run_worker as run_worker

client_list = []
message = 'Someone else just visited, or refreshed their browser.'
static_path_dir = './ace/public/'

def message_all(message):
    for client in client_list:
        client.write_message(message)

@route('/')
class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("public/index.html")
        message_all(message)

class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in client_list:
            client_list.append(self)

    def on_close(self):
        if self in client_list:
            client_list.remove(self)

@route('/load')
class LoadHandler(web.RequestHandler):
    def get(self):
        self.write(json.dumps({'code': database.load_from_mongo()}))

@route('/save')
class SaveHandler(web.RequestHandler):
    def post(self):
        database.save_to_mongo(escape.json_decode(self.request.body).get('code'))
        self.write(json.dumps({'message': 'Saved {} characters to MongoDB Cloud.'.format(len(database.load_from_mongo()))}))

@route('/run')
class RunHandler(web.RequestHandler):
    def post(self):
        print(self.request.body)
        self.write(run_worker.run(escape.json_decode(self.request.body)))

app = web.Application(route.get_routes()
    + [
        (r'/ws', SocketHandler),
        (r'/(.*)', web.StaticFileHandler, {'path': static_path_dir})
       ])