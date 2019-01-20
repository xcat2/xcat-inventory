###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
#
# xcat_exceptions.py 
#
# The xCAT client exceptions 
#
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


class XCATClientError(Exception):
    """Used to report XCAT client errors"""

    def __init__(self, req, message='', result=None):
        # The command request
        self.req = req

        # If error occurs before the command started, or after it ended,
        # the error message is stored here.
        self.message = message

        # If command finishes with error, the result is stored here.
        # The error and errorcode is stored inside the result.
        self.result = result

    def __str__(self):
        """Return a detailed error message"""

        if self.message:
            return 'Failed to run %s due to: %s' % (self.req.command, self.message)
        elif self.result and self.result.failed():
            return self.result.get_error_msg()
        else:
            return 'Failed to run %s due to: unknown error' % self.req.command
