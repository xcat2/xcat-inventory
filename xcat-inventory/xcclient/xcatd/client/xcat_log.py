###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
#
# xcat_log.py 
#
# Logging utilities to log trace and performance info
#

import os
import sys
import logging


# LOG UTILITIES

class CustomLogger(logging.Logger):

    def __init__(self, name):
        logging.Logger.__init__(self, name)
        lc_str = os.environ.get('FLASK_LOG_CLASSES', '')
        self._log_classes = dict.fromkeys(lc_str.split(), 1)

    def lc_debug(self, lc, msg, *args, **kwargs):
        """Log debug messages using a specified log class"""
        if self.isEnabledFor(logging.DEBUG) and lc in self._log_classes:
            # Get the frame where log message came from
            frm = sys._getframe(2)
            co = frm.f_code
            method = co.co_name

            # Determine if the log message came from a function or
            # a class method.
            if 'self' in frm.f_locals:
                clzname = frm.f_locals['self'].__class__.__name__
                method = '%s::%s()' % (clzname, method)
            
            self._log(logging.DEBUG, '%s:%s:%s' % (lc, method, msg), args, **kwargs)

    def trace(self, msg, *args, **kwargs):
        """Convenience method to log trace messages"""
        self.lc_debug('LC_TRACE', msg, *args, **kwargs)

    def perf(self, msg, *args, **kwargs):
        """Convenience method to log perf messages"""
        self.lc_debug('LC_PERF', msg, *args, **kwargs)
        

logging.setLoggerClass(CustomLogger)


def get_logger():
    # Return default logger
    log = logging.getLogger('ssl_util')
    fmt_str = "%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
    fmt = logging.Formatter(fmt_str)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    log.addHandler(ch)
    log.setLevel(logging.getLevelName("DEBUG"))
    return log

