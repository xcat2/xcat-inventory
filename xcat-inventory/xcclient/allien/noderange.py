###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os

class Noderange(object):
    def __init__(self, nr):
        self.nrstring = nr
        self.nodes = None

    def get_nodes(self):
        # here just for a fake testing
        if 'XCAT_NODES' in os.environ:
            self.nodes = os.environ.get('XCAT_NODES').split(',')
        else:
            self.nodes = ['fakenode01']

        return self.nodes
