###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

from .app import dbi
from .noderange import Noderange
from .nodemanager import get_hmi_by_list

try:
    from hwctl.executor.openbmc_power import OpenBMCPowerTask
except:
    from hwctl.openbmc.openbmc_power import OpenBMCPowerTask

from hwctl.power import DefaultPowerManager
from common.utils import Messager

# global variables of rpower
POWER_REBOOT_OPTIONS = ('boot', 'reset')
POWER_SET_OPTIONS = ('on', 'off', 'bmcreboot', 'softoff')
POWER_GET_OPTIONS = ('bmcstate', 'state', 'stat', 'status')


def rpower(nodelist, action):

    nodesinfo = get_hmi_by_list(nodelist)

    runner = OpenBMCPowerTask(nodesinfo, messager=Messager())
    if action == 'bmcstate':
        return DefaultPowerManager().get_bmc_state(runner)
    elif action == 'bmcreboot':
        DefaultPowerManager().reboot_bmc(runner)
    elif action in POWER_GET_OPTIONS:
        return DefaultPowerManager().get_power_state(runner)
    elif action in POWER_REBOOT_OPTIONS:
        return DefaultPowerManager().reboot(runner, optype=action)
    else:
        return DefaultPowerManager().set_power_state(runner, power_state=action)
