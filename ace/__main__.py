import os
from tornado import ioloop
from ace.routes import app

port = int(os.environ.get("PORT", 5000))
app.listen(port)
ioloop.IOLoop.instance().start()