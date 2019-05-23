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
    result={}
    paren_level = 0
    sign=0
    start=0
    end=0
    num=0
    for ch in input_str:
        if ch == '(':
            paren_level=paren_level+1
            if not sign:
                start=num
                sign=1
        elif (ch == ')') and paren_level:
            paren_level=paren_level-1
        if not paren_level and sign is 1:
            end=num+1
            break
        num=num+1

    result['prev']=input_str[:start]
    result['curr']=input_str[start:end]
    result['next']=input_str[end:]

    return result

def is_regexp_attr(attr):
    pattern=re.match('^\/[^\/]*\/[^\/]*\/$',attr) 
    if pattern:
        return 1

    pattern = re.match('^\|.*\|$', attr)
    if pattern:
        return 2

    return 0

def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

def trans_regex_attr(node,attr):
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
    is_reg=is_regexp_attr(attr)
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
        map_dict={}
        count=1
        while count <=len(matchvalue.groups()):
            tmpkey="$%s" % (count)
            map_dict[tmpkey]=matchvalue.group(count)
            count=count+1

        retval=multiple_replace(map_dict, retval)
        extractbracket=extract_bracketed(retval)
        #first replace expression
        curr=extractbracket['curr']
        prev=extractbracket['prev']
        nextt=extractbracket['next']
        while curr:
            value=eval(curr)
            retval="%s%s%s" % (prev,value,nextt)
            extractbracket=extract_bracketed(retval)
            curr=extractbracket['curr']
            prev=extractbracket['prev']
            nextt=extractbracket['next']
        
    return retval
