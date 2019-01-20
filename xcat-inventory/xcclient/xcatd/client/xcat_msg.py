###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-
#
# xcat_msg.py
# 
# Library to prepare xCAT request messages and parse xCAT response
# messages from xCAT daemon (xcatd).
#

import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

try:
    import xml.etree.cElementTree as etree
except ImportError:
    try:
        import xml.etree.ElementTree as etree
    except ImportError:
        try:
            from lxml import etree
        except ImportError:
            raise Exception("Failed to import ElementTree XML library")

from xml.parsers.expat import ExpatError

from .xcat_data import *

# 
# Classes for creating xCAT request messages
#


class XCATRequestBuilder(object):
    """Creates an XML request to run an xCAT command."""

    def to_xmlobj(self, xcat_req):
        """Returns the request as an ElementTree XML object"""

        r = xcat_req
        root = etree.Element("xcatrequest")
        etree.SubElement(root, "command").text = r.command

        if r.noderange:
            etree.SubElement(root, "noderange").text = r.noderange

        for arg in r.args:
            etree.SubElement(root, "arg").text = arg

        etree.SubElement(root, "cwd").text = r.cwd
        etree.SubElement(root, "clienttype").text = r.clienttype

        if r.table:
            etree.SubElement(root, "table").text = r.table

        for attr in r.attrs:
            etree.SubElement(root, "attr").text = attr

        if r.stdin:
            etree.SubElement(root, "stdin").text = r.stdin

        for k, v in r.env_vars.items():
            etree.SubElement(root, "env").text = '%s=%s' % (k, v)

        return root

    def to_string(self, xcat_req):
        """Returns the request as an XML string
           Example:
                <xcatrequest>
                  <command>makedns</command>
                  <noderange>compute1</noderange>
                  <arg>-d</arg>
                  <cwd>/tmp</cwd>
                  <clienttype>cli</clienttype>
                </xcatrequest>
        """
        root = self.to_xmlobj(xcat_req)
        return etree.tostring(root)+'\n'


# 
# Classes for parsing xCAT response messages
#

# Classes to parse primitive data


class XCATTableRowParser(object):

    def parse(self, elem):
        """Parses a single table row element (e.g., <row>, <node>, etc..)
        returned by xCAT table command, like getAllEntries

           Params: 
              An object representing a table row element:
              <row>
                <node>compute0</node>
                <groups>compute,all</groups>
              </row>

           Returns: XCATTableRow
        """

        to_return = XCATTableRow()

        for child_elem in elem:
            to_return[child_elem.tag] = child_elem.text

        return to_return


class XCATNodesetRecordParser(object):

    def parse(self, elem):
        """Parses a single <node> element returned by xCAT nodeset command

           Params: 
              An object representing a <node> element:
              <node>
                <data>boot</data>
                <destiny>boot</destiny>
                <imgserver>pcm-m100</imgserver>
                <name>compute0</name>
              </node>

           Returns:  XCATNodesetRecord 
        """

        to_return = XCATNodesetRecord()

        for child_elem in elem:
            if child_elem.tag == 'name':
                to_return.name = child_elem.text
            if child_elem.tag == 'imgserver':
                to_return.imgserver = child_elem.text
            if child_elem.tag == 'data':
                to_return.data = child_elem.text
            if child_elem.tag == 'destiny':
                to_return.destiny = child_elem.text
            if child_elem.tag == 'error':
                to_return.error = child_elem.text
            if child_elem.tag == 'errorcode':
                to_return.errorcode = child_elem.text

        return to_return


class XCATOutputMessageParser(object):

    def __init__(self, output_msg_tags=None):
        self._output_msg_tags = output_msg_tags or []

    def parse(self, elem):
        """Takes <xcatresponse> element produced by any xCAT command, 
           and parses the output message elements (e.g., <info>, <data>, 
           <contents>, etc..)

           If multiple output message elements exist under 
           <xcatresponse>, their string values are merged together 
           into one string, separated by newline.

           Params: 
              An object representing an <xcatresponse> element
            e.g.,
              <xcatresponse>
                 <info>1 object definitions have been created or modified.</info>
              </xcatresponse>

            e.g.,
              <xcatresponse>
                <data>Media copy operation successful</data>
              </xcatresponse>

            e.g.,
              <xcatresponse>
                  <data>
                    <contents>DNS setup is completed</contents>
                  </data>
              </xcatresponse>

           Returns: A string if one or more output elements 
                    were found.  Or NONE otherwise.
        """

        msg = ''

        for child_elem in elem.findall('.//*'):
            if child_elem.tag in self._output_msg_tags:
                msg += '%s\n' % child_elem.text

        msg = msg.rstrip()
        return msg


class XCATErrorParser(object):

    def parse(self, elem):
        """Takes <xcatresponse> element produced by any xCAT command, 
           and parses the <error> and <errorcode> child elements

           If there are multiple <error> elements under <xcatresponse>, 
           their error strings are merged together into one string, 
           separated by newlines.

           Params: 
              An object representing an <xcatresponse> element:
              <xcatresponse>
                 <error>Invalid nodes and/or groups in noderange: foobar </error>
                 <errorcode>1</errorcode>
                 <serverdone></serverdone>
              </xcatresponse>

           Returns: XCATErrorRecord if <error> or non-zero <errorcode> 
                    was found, or NONE otherwise.
        """

        error_msg = ''

        # Process <error> elements
        for error_elem in elem.findall('.//error'):
            # Handle xdsh bug: xdsh reboot/shutdown will return error on rhel7
            if not re.search('Connection to \w+ closed by remote host', error_elem.text):
                error_msg += '%s\n' % error_elem.text

        error_msg = error_msg.rstrip()

        if error_msg:
            # If we found one <error> element, locate its corresponding
            # <errorcode> element
            errorcode = '1'
            for errorcode_elem in elem.findall('.//errorcode'):
                errorcode = errorcode_elem.text
                break

            return XCATErrorRecord(error=error_msg, errorcode=errorcode)


# Classes to parse the results for different xCAT commands

class XCATGenericCmdResultParser(object):
    """Parses the basic info returned by an xCAT command.  This class
    is used to parse xCAT commands which return no data except for info 
    and error messages.  For xCAT commands which return more complex 
    data, you need to use one of the subclasses below to correctly 
    parse the result."""

    def __init__(self, req, raw_stream, output_msg_tags=None):
        """Initialize the parser 
           Params: 
                req:            XMLRequest object
                raw_stream:     Stream from which we read the XML response 
                output_msg_tags:  Names of XML tags which contain 
                                  output messages
        """
        self._req = req
        self._stream = \
            _XCATTagWrapperResponseStream(_XCATResponseStream(raw_stream))
        self._output_msg_tags = output_msg_tags or []
        self._output_msg_parser = XCATOutputMessageParser(output_msg_tags) 
        self._error_parser = XCATErrorParser()

    def parse(self):
        """Used to parse the basic info and error messages found in the 
        XML response of an xCAT command"""

        to_return = XCATGenericCmdResult()
        to_return.req = self._req

        try:
            context = etree.iterparse(self._stream, events=('end',))
            for action, elem in context:
                if elem.tag == 'xcatresponse':
                    output_msg = self._parse_output_msg(elem)
                    if output_msg:
                        to_return.output_msgs.append(output_msg)
                    error = self._parse_error(elem)
                    if error:
                        to_return.errors.append(error)
                    elem.clear()    
        except ExpatError as e:
            raise SyntaxError(str(e))
        except SyntaxError:
            raise    

        return to_return

    def _parse_output_msg(self, elem):
        """Helper method to parse output messages in xcatresponse tag"""

        return self._output_msg_parser.parse(elem)

    def _parse_error(self, elem):
        """Helper method to parse error in xcatresponse tag"""

        return self._error_parser.parse(elem)


class XCATTableCmdResultParser(XCATGenericCmdResultParser):
    """Parses the results of an xCAT table command"""

    def __init__(self, req, raw_stream, row_tag=''):
        """Initialize the parser 
           Params: 
                req:        XMLRequest object
                raw_stream: Stream from which we read the XML response 
                row_tag:    Name of XML tag which contains the 
                            table row data
        """
        XCATGenericCmdResultParser.__init__(self, req, raw_stream)
        self._row_tag = row_tag
        self._row_parser = XCATTableRowParser()

    def parse(self):
        """Used to parse the XML response of xCAT table command.  Each 
           row tag is parsed into an XCATTableRow object.  All objects
           are returned as part of XCATTableCmdResult object.

           Returns:  XCATTableCmdResult
           Exceptions:
                SyntaxError if XML parsing error occurs
                socket.error if fail to read from socket stream
        """

        to_return = XCATTableCmdResult()
        to_return.req = self._req
        to_return.table = self._req.table

        try:
            context = etree.iterparse(self._stream, events=('end',))
            for action, elem in context:
                # Process row tag, e.g., <row>
                if elem.tag == self._row_tag:
                    row = self._row_parser.parse(elem)
                    to_return.rows.append(row)
                    elem.clear()
                
                elif elem.tag == 'xcatresponse':
                    error = self._parse_error(elem)
                    if error:
                        to_return.errors.append(error)
                    elem.clear()
        except ExpatError as e:
            raise SyntaxError(str(e))
        except SyntaxError:
            raise
                
        return to_return


class XCATNodesetCmdResultParser(XCATGenericCmdResultParser):
    """Parses the results of xCAT nodeset command"""

    def __init__(self, req, raw_stream):
        """Initialize the parser 
           Params: 
                req:        XMLRequest object
                raw_stream: Stream from which we read the XML response 
        """
        XCATGenericCmdResultParser.__init__(self, req, raw_stream)
        self._nodeset_rec_parser = XCATNodesetRecordParser()

    def parse(self):
        """Used to parse the XML response of xCAT nodeset command.  Each 
           node tag is parsed into an XCATNodesetRecord object.  
           All objects are returned as part of XCATNodesetCmdResult 
           object.

           Returns:  XCATNodesetCmdResult
           Exceptions:  
                SyntaxError if XML parsing error occurs
                socket.error if fail to read from socket stream
        """

        to_return = XCATNodesetCmdResult()
        to_return.req = self._req

        try:
            context = etree.iterparse(self._stream, events=('end',))
            for action, elem in context:
                # Process <node> tag
                if elem.tag == 'node':
                    node = self._nodeset_rec_parser.parse(elem)
                    to_return.node_dict[node.name] = node
                    if node.error:
                        to_return.failed_nodes.append(node.name)
                    else:
                        to_return.success_nodes.append(node.name)
    
                    elem.clear()
                
                elif elem.tag == 'xcatresponse':
                    error = self._parse_error(elem)
                    if error:
                        to_return.errors.append(error)
    
                    elem.clear()

        except ExpatError as e:
            raise SyntaxError(str(e))
        except SyntaxError:
            raise    

        return to_return


# 
# Helper classes for reading and formatting the XML response 
# from a data stream
#

class _XCATResponseStream(object):
    """Wraps an existing data stream like an SSL connection, XML file, 
    StringIO object, etc. and provides a new read() method which stops 
    reading when the end of the xCAT response is reached."""

    def __init__(self, raw_stream):
        self._raw_stream = raw_stream
        self._last_1KB_data = ''

    def read(self, size):
        """Returns some of the raw response data up to the max size.  
        The caller is responsible for calling this method as many times
        as needed to get the full data.
           Params:
                size: Set to integer > 0
           Returns:
                String containing a part of the response string, or 
                an empty string when there is no more data to read.
           Exception:
                socket.error: if socket error occurs or read 
                operation times out.
        """

        # If we already read the end of the response, then return
        # empty string
        data = self._last_1KB_data
        serverdone = data.find('<serverdone>')
        if serverdone > -1:
            if data[serverdone:].find('</serverdone>') > -1 and \
               data[serverdone:].find('</xcatresponse>') > -1:
                return ''

        to_return = self._raw_stream.read(size)
        
        # Save the last 1KB of data read. We use this to 
        # check whether we reached the end of the response data.
        self._last_1KB_data += to_return
        self._last_1KB_data = self._last_1KB_data[-1024:]

        return to_return


class _XCATTagWrapperResponseStream(object):
    """Wraps an _XCATResponseStream object and provides a new read() 
    method which wraps the original xCAT response inside 
    a <xcatresponsewrapper> tag.  

    The new response string looks like this:

        <xcatresponsewrapper>
            ... raw xCAT XML data
        </xcatresponsewrapper>
    """

    def __init__(self, xcat_raw_stream):
        self._streams = [StringIO('<xcatresponsewrapper>'),
                         xcat_raw_stream,
                         StringIO('</xcatresponsewrapper>')]

    def read(self, size):
        """Returns some of the re-formatted response data up to the 
           max size. The caller is responsible for calling this method 
           as many times as needed to get the full data.  
           Params:
                size: Set to integer > 0
           Returns:
                String containing a part of the response string, or 
                an empty string when there is no more data to read.
           Exception:
                socket.error: if socket error occurs or read 
                operation times out.
        """
        if size <= 0:
            raise Exception('Programming error: you must specify size > 0.')

        to_read = size
        to_return = ''

        # Read the data from each stream in the list
        for stream in self._streams:
            while to_read > 0:
                buf = stream.read(to_read)
                if len(buf) == 0:
                    # No more data to read from this stream,
                    # Try the next one ...
                    break
                else:
                    to_return += buf
                    to_read -= len(buf)

        return to_return
