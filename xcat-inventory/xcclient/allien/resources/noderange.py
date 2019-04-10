###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import current_app
from flask_restplus import Resource
from xcclient.allien.nodemanager import get_nodes_by_range


class NodeRangeResource(Resource):

    def get(self, nr):
        return get_nodes_by_range(nr)