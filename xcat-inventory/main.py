#!/usr/bin/env python
###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import sys
# Set path for openbmc-py
if '/opt/xcat/lib/python' not in sys.path:
    sys.path.insert(1, '/opt/xcat/lib/python')

from gevent import monkey
monkey.patch_all()

from xcclient.allien.app import create_app
from xcclient.inventory.shell import main

# Main entry without external WSGI server
if __name__ == "__main__":

    if len(sys.argv) > 1:
        sys.exit(main())

    app = create_app()
    if app.debug:
        app.run(host="0.0.0.0")
    else:
        from gevent.pywsgi import WSGIServer
        http_server = WSGIServer(("0.0.0.0", 5000), app)
        http_server.serve_forever()
