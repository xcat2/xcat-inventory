###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
#
# xcat_client_base.py 
#
# Base class for the xCAT client (xcat_client.py).
#

from .xcat_exceptions import *
from .xcat_ssl import *
from .xcat_msg import *


class XCATClientBase(object):
    """Base class for creating a client to run xCAT commands."""

    #
    # Utility methods
    #

    def _init(self, logger, params, default_sockopts, cmd_sockopts):
        """Initialize the client object."""

        self._logger = logger

        self._host = params.host
        self._port = params.port
        self._ca_certs = params.ca_certs
        self._client_cred = params.client_cred
        self._reuse_connection = params.reuse_connection
        self._default_sockopts = default_sockopts
        self._cmd_sockopts = cmd_sockopts
        
        if self._reuse_connection:
            self._reused_ssl_client = self._create_ssl_client(logger, default_sockopts)
        else:
            self._reused_ssl_client = None

    def _create_ssl_client(self, logger, sockopts):
        """Create a new SSL client 
           Returns: SSLClient object
        """

        ssl_sockopts = self._convert_to_ssl_sockopts(sockopts)
        return SSLClient(logger, ssl_sockopts)

    def _convert_to_ssl_sockopts(self, client_sockopts):
        """Convert XCATClientSocketOptions object to SSLClientSocketOptions object 
           Params: XCATClientSocketOptions object
           Returns: SSLClientSocketOptions object"""

        s = SSLClientSocketOptions()
        c = client_sockopts

        s.connect_timeout_sec = c.connect_timeout_sec
        s.connect_attempts = c.connect_attempts
        s.read_timeout_sec = c.read_timeout_sec
        s.read_attempts = c.read_attempts
        s.write_timeout_sec = c.write_timeout_sec
        s.write_attempts = c.write_attempts

        return s

    def _get_ssl_sockopts(self, command):
        c = self._cmd_sockopts.get(command, self._default_sockopts)
        return self._convert_to_ssl_sockopts(c)        

    def _cleanup(self):
        """Cleanup the client object."""

        self._logger = None

        self._host = None
        self._port = None
        self._ca_certs = None
        self._client_cred = None
        self._default_sockopts = None
        self._cmd_sockopts = None

        if self._reuse_connection:
            self._reused_ssl_client.disconnect()

        self._reuse_connection = False
        self._reused_ssl_client = None

    def _run_command(self, cmd_helper):
        """Utility method to run xCAT commands using SSL"""

        try:
            return self._run_command_helper(cmd_helper)
        except XCATClientError:
            raise
        except (socket.error, SyntaxError) as e:
            self._logger.exception(e)
            req = cmd_helper.get_request()
            raise XCATClientError(req, message=str(e)) 

    def _run_command_helper(self, cmd_helper):

        do_client_disconnect = False
        ssl_client = None

        self._logger.debug(str(cmd_helper))

        try:
            # Get socket options for the xCAT command we will run
            ssl_sockopts = self._get_ssl_sockopts(cmd_helper.command)
            
            # Create SSL client
            if self._reuse_connection:
                # Reuse existing client
                ssl_client = self._reused_ssl_client
                ssl_client.set_sockopts(ssl_sockopts)
                do_client_disconnect = False
            else:
                # Create new client
                ssl_client = self._create_ssl_client(self._logger, ssl_sockopts)
                do_client_disconnect = True

            # Connect to SSL server. If already connected, this is a no-op.
            ssl_client.connect(self._host, self._port, self._ca_certs, self._client_cred)
            
            # Submit request
            req = cmd_helper.get_request()
            req_str = XCATRequestBuilder().to_xml(req)
            ssl_client.write_all(req_str)

            # Parse response
            result = cmd_helper.parse_response(ssl_client)
            if result.failed():
                req = cmd_helper.get_request()
                raise XCATClientError(req, result=result)
            
        finally:
            # Cleanup SSL connection
            if do_client_disconnect and ssl_client:
                ssl_client.disconnect()
                ssl_client = None
                ssl_sockopts = None

        return result
