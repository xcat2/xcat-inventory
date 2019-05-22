###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import os
import random
import uuid

from flask import g, current_app

from xcclient.xcatd import XCATClient, XCATClientParams

from .invmanager import ParseException


def provision(nr, action_spec=None):
    """Helper method to parse payload and do rintall"""

    boot_state = 'osimage'
    target =  None
    if action_spec:
        if 'osimage' in action_spec and action_spec.get('osimage'):
            target = "osimage=%s" % action_spec['osimage']

        if 'boot_state' in action_spec and target:
            raise ParseException('Do not specify multiple boot target.')
        elif not target:
            target = action_spec.get('boot_state')

    boot_state = target or boot_state
    # TODO: support more args later

    param = XCATClientParams(xcatmaster=os.environ.get('XCAT_SERVER'))
    cl = XCATClient()
    cl.init(current_app.logger, param)
    cl.makedns(noderange=nr)
    result = cl.rinstall(noderange=nr, boot_state=boot_state)
    return result.output_msgs
