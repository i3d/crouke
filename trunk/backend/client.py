#!/usr/bin/env python

"""Client api for api.gnome-look.org and all opendesktop.org sites.

Privde CRUD methods to manipulate content feeds.
"""

# system library
import base64
import httplib
import re
import sys
sys.path.append('..')

# Crouke library
from objectifyxml import ContentParser
import excepts

pattern = re.compile(r'/V1/(\w+)/(.*?)')


def GetCategoryType(url):
    """Retrieve the string reprsenting the feed category type.

    Args:
        url: a url string that used to retrieve the content feed.

    Returns:
        A string reprsenting the feed category type.
    """
    m = pattern.match(url)
    return m.groups()[0]


def GetElementTagFromData(data):
    """Return the xml tag names in an element.

    Args:
        data: an xml element.

    Returns:
        A list of tag names for a given element.
    """
    return [i.tag for i in data.GetElementData().getiterator()][1:]


class DefaultCRUDHandler(object):
    """Provide a default CRUD handler.
    """

    def __init__(self, server=None, headers=None, raw=False):
        """Constructor to init the object.

        Args:
            server: the target server.
            headers: http headers.
            raw: boolean whether send back raw HTTPResponse data.
        """
        self._server = server
        self._headers = headers
        self._raw = raw

    def Get(self, url, *args, **kws):
        """Retrieve the content feed for a given url.

        Args:
            url: the url for the content feed.
            extra_headers: any extra_headers needs to be added.
            raw: boolean whether or not return the raw response data.
                 If False, the feed will be fed into the Objectify module
                 to form an feed object.

        Returns:
            Either a HTTPResponse object (file like) or 
            an object reprsenting the feed (converted by objectify).
        """
        if 'headers' in kws:
            headers = kws['headers']
        else:
            headers = self._headers

        if 'server' in kws:
            server = kws['server']
        else:
            server = self._server

        if 'raw' in kws:
            raw = kws['raw']
        else:
            raw = self._raw

        conn = httplib.HTTPConnection(server)
        conn.request('GET', url, None, headers)
        resp = conn.getresponse()
        if raw:
            return resp
        else:
            try:
                feed = ContentParser(resp.read(),
                              GetCategoryType(url)).objectify()
            except (SyntaxError, TypeError), e:
                raise excepts.RequestHandlingError(e)
        return feed


class CroukeClient(object):
    """Provide basic CROD handling for opendesktop.org sites api.

    Currently, since the api only has GET, we only provide a Get method.
    The actual implemention for the Get is provided by the handler instance.
    With loose coupling, others can develop CRUD methods and register them 
    into their client object for their own CRUD requirements.
    """

    _CRUD = {'Get': [], 'Post': [], 'Put': [], 'Delete': []}

    def __init__(self, user=None, password=None, server=None, headers=None, 
                 extra_headers=None, *args, **kws):
        """Constructor to initial the object.

        Args:
            user: the login username.
            password: the login password.
            server: which api server it should connect to.
        """
        self._server = server
        self._headers = headers
        if not self._headers and (user and password):
            self._headers = {'authorization' :
            'Basic ' + base64.encodestring('%s:%s' % (user, password))}
        if extra_headers:
            for k, v in extra_headers.iteritems():
                self._headers[k] = v
        self._args = args
        self._kws = kws
        self._logger = None

    def RegisterHandlers(self, crud_type, handlers):
        """Register CRUD request/response handler.
        
        Args:
            curd_type: 'Get', 'Post', 'Put', or 'Delete'
            handlers: the callback when an cooresponding request
                      is called.
                      When error encountered, the handler
                      needs to raise excepts.RequestHandlingError error.
        """
        if not isinstance(handlers, (list, tuple)):
            self._CRUD[crud_type].append(handlers)
        else:
            self._CRUD[crud_type].extend(handlers)

    def RegisterLogHandler(self, logger):
        """Register a logging facility.

        Args:
            logger: a logging object that provides a log method.
        """
        self._logger = logger

    def Get(self, url, *args, **kws):
        """Retrieve the content feed for a given url.

        Args:
            url: the url for the content feed.
            args: extra args.
            kws: extra keyword args.

        Returns:
            The actual handler returns.
        """
        for handler in self._CRUD['Get']:
            try:
                resp = handler.Get(url, *args, **kws)
            except excepts.RequestHandlingError, e:
                if self._logger:
                    self._logger.log(e)
                else:
                    print >> sys.stderr, e
            else:
                return resp

    def Post(self, url, *args, **kws):
        """Post the content feed to a given url.

        Args:
            url: the url for the content feed.
            args: extra args.
            kws: extra keyword args.

        Returns:
            The actual handler returns.
        """
        for handler in self._CRUD['Post']:
            try:
                resp = handler.Post(url, *args, **kws)
            except excepts.RequestHandlingError, e:
                if self._logger:
                    self._logger.log(e)
                else:
                    print >> sys.stderr, e
            else:
                return resp

    def Put(self, url, *args, **kws):
        """Put the content feed to a given url.

        Args:
            url: the url for the content feed.
            args: extra args.
            kws: extra keyword args.

        Returns:
            The actual handler returns.
        """
        for handler in self._CRUD['Put']:
            try:
                resp = handler.Put(url, *args, **kws)
            except excepts.RequestHandlingError, e:
                if self._logger:
                    self._logger.log(e)
                else:
                    print >> sys.stderr, e
            else:
                return resp

    def Delete(self, url, *args, **kws):
        """Delete the content feed to a given url.

        Args:
            url: the url for the content feed.
            args: extra args.
            kws: extra keyword args.

        Returns:
            The actual handler returns.
        """
        for handler in self._CRUD['Delete']:
            try:
                resp = handler.Delete(url, *args, **kws)
            except excepts.RequestHandlingError, e:
                if self._logger:
                    self._logger.log(e)
                else:
                    print >> sys.stderr, e
            else:
                return resp

