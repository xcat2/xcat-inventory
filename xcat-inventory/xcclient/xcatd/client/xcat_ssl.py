###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
#
# xcat_ssl.py 
#
# SSL client library. 
#
# It uses the pyOpenSSL module for SSL by default.  If this 
# module is not installed, it uses the built-in ssl module 
# which is available in Python 2.6 and higher.
# 

import os
import sys
import socket
import select
import pprint
import copy
import time

from .timer import Timer

try:
    import ssl
except ImportError:
    try:
        from OpenSSL import SSL
    except ImportError:
        raise Exception("This module requires SSL support.  You must install the pyOpenSSL package or install Python version 2.6 or higher.")


class BuiltInSSLSocket(object):

    def __init__(self, host, port, ca_certs, client_cred, connect_timeout):
        self._sock = ssl.wrap_socket(socket.socket(socket.AF_INET, 
                socket.SOCK_STREAM), cert_reqs=ssl.CERT_REQUIRED,
                ca_certs=ca_certs, certfile=client_cred, 
                ssl_version=ssl.PROTOCOL_TLSv1)
        self._sock.settimeout(connect_timeout)
        self._sock.connect((host, port)) 
        self._sock.settimeout(None)

    def __str__(self):
        m  = '\nSSL module: Built-in'
        m += '\nSSL server: %s' % repr(self._sock.getpeername())
        m += '\nSSL server ciphers: %s' % repr(self._sock.cipher())
        m += '\nSSL server certificate: %s\n' % pprint.pformat(self._sock.getpeercert())
        return m

    def fileno(self):
        return self._sock.fileno()

    def read(self, size):
        return self._sock.read(size)

    def write(self, msg):
        return self._sock.write(msg)

    def shutdown(self):
        return self._sock.shutdown(socket.SHUT_RDWR)

    def close(self):
        return self._sock.close()


class PyOpenSSLSocket(object):

    def __init__(self, host, port, ca_certs, client_cred, connect_timeout):
        ctx = SSL.Context(SSL.SSLv3_METHOD)
        ctx.use_privatekey_file(client_cred)
        ctx.use_certificate_file(client_cred)
        ctx.load_verify_locations(ca_certs)

        self._sock = SSL.Connection(ctx, socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM))
        self._sock.settimeout(connect_timeout)
        self._sock.connect((host, port))
        self._sock.settimeout(None)

    def __str__(self):
        m  = '\nSSL module: PyOpenSSL'
        m += '\nSSL server: %s' % repr(self._sock.getpeername())
        return m

    def fileno(self):
        return self._sock.fileno()

    def read(self, size):
        return self._sock.read(size)

    def write(self, msg):
        return self._sock.write(msg)

    def shutdown(self):
        return self._sock.shutdown()

    def close(self):
        return self._sock.close()


class SSLClientSocketOptions(object):
    """Set of options to control socket oeprations"""

    def __init__(self):
        # Number of seconds to wait before retrying connection
        self.connect_timeout_sec = -1

        # Number of socket connection attempts before failing 
        self.connect_attempts = 1

        # Number of seconds to wait before retrying socket read
        self.read_timeout_sec = -1

        # Number of socket read attempts before failing
        self.read_attempts = 1

        # Number of seconds to wait before retrying socket write
        self.write_timeout_sec = -1

        # Number of socket write attempts before failing
        self.write_attempts = 1

    def __str__(self):
        return "connect:timeout=%s,attempts=%s, read:timeout=%s,attempts=%s, write:timeout=%s,attempts=%s" % \
            (self.connect_timeout_sec, self.connect_attempts,
             self.read_timeout_sec, self.read_attempts,
             self.write_timeout_sec, self.write_attempts)


class SSLClient(object):

    def __init__(self, logger, sockopts):
        """Create a new SSL client
           Params:
                logger:    Pre-created logger object
                sockopts:  SSL socket options (SSLClientSocketOptions object)
        """
        self._logger = logger
        self._ssl_sock = None
        self._sockopts = sockopts
        self._logger.trace('Init SSL options: %s' % str(sockopts))

    def get_sockopts(self):
        return copy.copy(self.sockopts)

    def set_sockopts(self, sockopts):
        """Change the SSL socket options (SSLClientSocketOptions object)"""
        self.sockopts = copy.copy(sockopts)
        self._logger.trace('Updated SSL options: %s' % str(sockopts))

    def is_connected(self):
        """Check if SSL client is connected to SSL server"""
        return self._ssl_sock != None

    def is_disconnected(self):
        """Check if SSL client is not connected to SSL server"""
        return self._ssl_sock == None


    def connect(self, host, port, ca_certs, client_cred):
        """Create a new connection to the SSL server
           Params:
                host:        Hostname or IP address of SSL server (str)
                port:        Port of SSL server (str)
                ca_certs:    Path of file containing CA certificates to 
                             verify server certificate is signed by 
                             legitimate authority (str)
                client_cred: Path of file containing client certificate and 
                             private key (str)
           Exception:
                socket.error: if socket connection error occurs or
                connection times out.
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # Error-checking
            if not host:
                raise Exception('Programming error: you must specify a non-empty host')
            elif not port:
                raise Exception('Programming error: you must specify a non-empty port')
            elif not ca_certs:
                raise Exception('Programming error: you must specify a non-empty ca_certs')
            elif not client_cred:
                raise Exception('Programming error: you must specify a non-empty client_cred')
            elif self._ssl_sock:
                # Do not connect again if connection already exists.
                self._logger.trace('Connection not created as it already exists.')
                return

            # Connect
            self._connect_with_retry(host, port, ca_certs, client_cred)
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')


    def write(self, msg):
        """Send a message to the SSL server. It is possible for only 
           some of the message to be sent.  The caller is responsible
           for calling write() as many times as needed until the data 
           is fully sent.
           Params:
                msg:  Set to non-empty string
           Returns:
                Number of bytes written
           Exception:
                socket.error: if socket error occurs or write 
                operation times out.
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # Error-checking
            if not msg:
                raise Exception('Programming error: you must specify a non-empty message')
            elif not self._ssl_sock:
                raise Exception('Programming error: you must connect before writing a message.')

            # Write
            if len(msg) > 10240:
                self._logger.trace('Attempting to write: \n%s ...' % str(msg[:10240]).rstrip())
            else:
                self._logger.trace('Attempting to write: \n%s' % str(msg).rstrip())

            return self._write_with_retry(msg)
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def write_all(self, msg):
        """Convenience method to ensure that a message is fully sent 
           to the SSL server.
           Params:
                msg:  Set to non-empty string
           Returns:
                Number of bytes written
           Exception:
                socket.error: if socket error occurs or write 
                operation times out.
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # Error-checking
            if not msg:
                raise Exception('Programming error: you must specify a non-empty message')
            elif not self._ssl_sock:
                raise Exception('Programming error: you must connect before writing a message.')

            # Write
            self._logger.trace('Attempting to write: \n%s' % str(msg).rstrip())
            return self._write_all(msg)
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def read(self, size):
        """Read the response data from the SSL server up to a max size.
           The size returned may be less than max size.  The caller is 
           responsible for calling read() as many times as needed until 
           the data is fully received.
           Params: 
                size:  Set to integer > 0
           Returns:
                A string containing the received data
           Exception:
                socket.error: if socket error occurs or read 
                operation times out.
        """
        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            # Error-checking
            if size <= 0:
                raise Exception('Programming error: you must specify size > 0.')
            elif not self._ssl_sock:
                raise Exception('Programming error: you must connect before reading a message.')

            # Read
            msg = self._read_with_retry(size)
            if len(msg) > 10240:
                self._logger.trace('Message read: \n%s ...' % str(msg[:10240]).rstrip())
            else:
                self._logger.trace('Message read: \n%s' % str(msg).rstrip())
            return msg
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def disconnect(self):
        """Disconnect from the SSL server"""

        try:
            self._logger.trace('Entering')
            t = Timer().start_timer()
            if not self._ssl_sock:
                # We're already disconnected, so this is a no-op.
                return
            self._disconnect()
        finally:
            t.stop_timer()
            self._logger.perf('%s msec' % t.get_elapsed_in_msec())
            self._logger.trace('Leaving')

    def _connect_with_retry(self, host, port, ca_certs, client_cred):

        attempts = self._sockopts.connect_attempts
        connect_timeout = self._sockopts.connect_timeout_sec
        last_error = ''

        for n in range(1, attempts+1):
            self._logger.trace('Connection attempt %s of %s' % (n, attempts))
            t = Timer().start_timer()
            try:
                self._connect_once(host, port, ca_certs, client_cred)
                return
            except (socket.error, socket.timeout) as e:
                last_error = str(e)

            self._logger.trace('Connection attempt %s of %s failed: %s' % (n, attempts, last_error))

            if n == attempts:
                break

            # If connect attempt returned before timeout expired, just sleep
            # for the time difference before retrying
            t.stop_timer()
            diff = connect_timeout - t.get_elapsed_in_sec()
            if diff > 0:
                self._logger.trace('Sleeping for %s sec before next attempt' % diff)
                time.sleep(diff)

        self._logger.trace('All connection attempts failed.')
        raise socket.error(last_error)

    def _connect_once(self, host, port, ca_certs, client_cred):
        connect_timeout = self._sockopts.connect_timeout_sec

        self._logger.trace('Before create:' + \
                           '\nSSL host/port: %s/%s' % (host, port) + \
                           '\nCA certs file: %s' % ca_certs + \
                           '\nClient cred file: %s' % client_cred)

        if globals().has_key('SSL'):
            self._ssl_sock = PyOpenSSLSocket(host, port, ca_certs, client_cred, connect_timeout)
        else:
            self._ssl_sock = BuiltInSSLSocket(host, port, ca_certs, client_cred, connect_timeout)

        self._logger.trace('After create:' + str(self._ssl_sock))

    def _write_all(self, msg):

        # Do the write
        to_write = len(msg)
        total_written = 0

        while to_write > 0:
            written = self._write_with_retry(msg)
            total_written += written
            to_write -= written
            msg = msg[written:]

        return total_written

    def _write_with_retry(self, msg):

        attempts = self._sockopts.write_attempts
        write_timeout = self._sockopts.write_timeout_sec
        last_error = ''

        for n in range(1, attempts+1):
            self._logger.trace('Write attempt %s of %s' % (n, attempts))
            t = Timer().start_timer()
            try:
                return self._write_once(msg)
            except (socket.error, socket.timeout) as e:
                last_error = str(e)

            self._logger.trace('Write attempt %s of %s failed: %s' % (n, attempts, last_error))

            if n == attempts:
                break

            # If write attempt returned before timeout expired, just sleep
            # for the time difference before retrying
            t.stop_timer()
            diff = write_timeout - t.get_elapsed_in_sec()
            if diff > 0:
                self._logger.trace('Sleeping for %s sec before next attempt' % diff)
                time.sleep(diff)

        self._logger.trace('All write attempts failed.')
        raise socket.error(last_error)

    def _write_once(self, msg):

        write_timeout = self._sockopts.write_timeout_sec

        # Do the write
        self._logger.trace('Attempting to write: %s bytes' % len(msg))

        output = [self._ssl_sock.fileno()]

        try:
            in_ready, out_ready, ex_ready = select.select([], output, [], write_timeout)
            bytes_written = self._ssl_sock.write(msg)
            self._logger.trace('Wrote: %s bytes' % bytes_written)
            return bytes_written
        except (select.error, socket.timeout) as e:
            raise socket.error(str(e))

    def _read_with_retry(self, size):

        attempts = self._sockopts.read_attempts
        read_timeout = self._sockopts.read_timeout_sec
        last_error = ''

        for n in range(1, attempts+1):
            self._logger.trace('Read attempt %s of %s' % (n, attempts))
            t = Timer().start_timer()
            try:
                return self._read_once(size)
            except (socket.error, socket.timeout) as e:
                last_error = str(e)

            self._logger.trace('Read attempt %s of %s failed: %s' % (n, attempts, last_error))

            if n == attempts:
                break

            # If read attempt returned before timeout expired, just sleep
            # for the time difference before retrying
            t.stop_timer()
            diff = read_timeout - t.get_elapsed_in_sec()
            if diff > 0:
                self._logger.trace('Sleeping for %s sec before next attempt' % diff)
                time.sleep(diff)

        self._logger.trace('All read attempts failed.')
        raise socket.error(last_error)

    def _read_once(self, size):

        read_timeout = self._sockopts.read_timeout_sec

        # Do the read
        self._logger.trace('Attempting to read: %s bytes' % size)

        input = [self._ssl_sock.fileno()]
        to_read = size
        to_return = ''

        try:
            in_ready, out_ready, ex_ready =  select.select(input, [], [], read_timeout)
            to_return = self._ssl_sock.read(to_read)
        except (select.error, socket.timeout) as e:
            raise socket.error( str(e) )

        self._logger.trace('Read: %s bytes, Requested: %s bytes' % (len(to_return), to_read))

        return to_return

    def _disconnect(self):
        try:
            self._ssl_sock.shutdown()
        except socket.error as e:
            self._logger.warn('Failed to shutdown SSL socket')

        try:
            self._ssl_sock.close()
        except socket.error as e:
            self._logger.warn('Failed to close SSL socket')

        self._ssl_sock = None

