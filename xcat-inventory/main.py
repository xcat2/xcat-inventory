###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import time
from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer
from xcclient.allien.app import create_app


#@app.route('/table', methods=['GET'])
#def test():
#    return jsonify(dbi.gettab(['site']))

if __name__ == "__main__":

    app = create_app()
    app.run()
    #http_server = WSGIServer(('', 5000), app)
    #http_server.serve_forever()
