###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
from flask import g, current_app

from xcclient.xcatd import XCATClient, XCATClientParams


def provision(nr, target='osimage', param=None):
    """provision nodes"""

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    result = cl.rinstall(noderange=nr, boot_state=target)
    return result.output_msgs
