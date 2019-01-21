###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import sys
# Set path for openbmc-py
sys.path.insert(0, '/opt/xcat/lib/python/agent')

from gevent import monkey
monkey.patch_all()

from xcclient.allien.app import create_app

# Main entry without external WSGI server
if __name__ == "__main__":

    app = create_app()
    if app.debug:
        app.run()
    else:
        from gevent.pywsgi import WSGIServer
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
