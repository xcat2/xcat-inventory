###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

#
# These are constants used by xCAT client library, need to get them from config file
#

#
# Default client SSL parameters
#

XCAT_HOST = 'localhost'
XCAT_SSL_PORT = 3001
XCAT_SSL_CA_CERTS = '/root/.xcat/ca.pem'
XCAT_SSL_CLIENT_CRED = '/root/.xcat/client-cred.pem'

#
# Default client socket options
#

# Retry connection failures for up to 1 min
XCAT_CLIENT_CONNECT_TIMEOUT_SEC = 12
XCAT_CLIENT_CONNECT_ATTEMPTS = 5

# Retry read failures for up to 5 mins
XCAT_CLIENT_READ_TIMEOUT_SEC = 60
XCAT_CLIENT_READ_ATTEMPTS = 5

# Retry write failures for up to 1 min
XCAT_CLIENT_WRITE_TIMEOUT_SEC = 12
XCAT_CLIENT_WRITE_ATTEMPTS = 5

