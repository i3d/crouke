#!/usr/bin/env python

"""
"""

# system library
import base64
import httplib
import re

# Crouke library
from objectifyxml import ContentParser

pattern = re.compile(r'/V1/(\w+)/(.*?)')

def GetCategory(url):
    """
    """
    m = pattern.match(url)
    return m.groups()[0]

def GetElementTagFromData(data):
    """
    """
    return [i.tag for i in data.GetElementData().getiterator()][1:]

class CroukeClient(object):
    """
    """
    def __init__(self, user, password, server):
        """
        """
        self._server = server
        self._user = user
        self._password = password
        self._headers = {'authorization' :
            'Basic ' + base64.encodestring('%s:%s' %
            (self._user, self._password))}

    def Get(self, url, extra_headers=None, raw=False):
        """
        """
        if extra_headers:
            for k, v in extra_headers.iteritems():
                self._headers[k] = v
        conn = httplib.HTTPConnection(self._server)
        conn.request('GET', url, None, self._headers)
        resp = conn.getresponse()
        if raw: return resp
        else: return ContentParser(resp.read(), GetCategory(url)).objectify()
