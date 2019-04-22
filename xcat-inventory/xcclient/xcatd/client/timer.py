###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import time

# TIMER UTILITIES


class Timer(object):

    def __init__(self):
        self._start_time = None
        self._end_time = None

    def start_timer(self):
        self._start_time = time.time()
        return self

    def stop_timer(self):
        self._end_time = time.time()

    def get_elapsed_in_msec(self):
        diff = self._end_time - self._start_time
        return float(round(diff * 100000)) / 100

    def get_elapsed_in_sec(self):
        diff = self._end_time - self._start_time
        return float(round(diff * 100)) / 100

