###############################################################################
# IBM(c) 2019 EPL license http://www.eclipse.org/legal/epl-v10.html
###############################################################################

# -*- coding: utf-8 -*-

import re

def extract_bracketed(input_str):
    """extract bracketed expression into dict
       input_str example: 10.($1+1).0.($2+3)
       output example:
        { 'prev': '10.',
          'curr': '($1+1)',
          'next': '.0.($2+3)'
        }

    """
    result = {}
    pre=''
    cur=''
    nxt=''
    sign = 0
    loop=0
    for ch in input_str:
        if sign is not 2:
            if ch == '(':
                sign=1
            elif (ch == ')'):
                sign=2
                loop+=1
                if loop is 1:
                    cur += ch
                    ch=''
                    loop=0
        if sign is 1:
            cur += ch
        elif sign is 2 and ch:
            nxt += ch
        elif sign is 0:
            pre += ch
    result['prev']=pre
    result['curr']=cur
    result['next']=nxt
    return result

def is_regexp(attr):
    pattern=re.match('^\/[^\/]*\/[^\/]*\/$',attr) 
    if pattern:
        return 1

    pattern = re.match('^\|.*\|$', attr)
    if pattern:
        return 2

    return 0

def trans_regex_attrs(node,attr):
    """Transform the regular expression attribute to the target value
       based on the node name.

    Arguments:
            Node
            Attribute value (may have regular expression):
            example1: '/txtxtx/1.1.1.1/'
            example2: '|\D+(\d+)|10.0.0.($1+10)|
    Return:
            Attribute value
    """
    retval=attr
    is_reg=is_regexp(attr)
    if is_reg is 1:
        exp=attr[0]
        parts=attr[1:-1].split(exp)
        retval=re.sub(parts[0], parts[1], node)

    if is_reg is 2:
        exp=attr[0]
        parts=attr[1:-1].split(exp)
        partslen=len(parts)
        #easy regx, generate lhs from node
        if partslen < 2:
            numbers=re.search('[\D0]*(\d+)',node)
            lhs='[\D0]*(\d+)'*len(numbers)
            lhs+='.*$'
            parts.append(lhs)
        #find all matched value
        matchvalue=re.search(parts[0],node)
        #handle replace expression
        retval=parts[1]
        extractbracket=extract_bracketed(retval)
        #first replace expression
        curr=extractbracket['curr']
        prev=extractbracket['prev']
        nextt=extractbracket['next']
        while curr:
            tmpexp=re.sub(r'(\$\d+)', r'int(matchvalue.group(\1))', curr)
            validexp=re.sub(r'(\$)', '', tmpexp)
            value=eval(validexp)
            retval="%s%s%s" % (prev,value,nextt)
            extractbracket=extract_bracketed(retval)
            curr=extractbracket['curr']
            prev=extractbracket['prev']
            nextt=extractbracket['next']
        
    return retval
