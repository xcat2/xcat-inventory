###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from flask_restful import Resource
from xcclient.allien.app import dbi
from xcclient.allien.resources import api

@api.resource('/site')
class SiteResource(Resource):
    def get(self):
        return dbi.gettab(['site'])

