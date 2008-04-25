#!/usr/bin/env python

"""
"""

import __builtin__ as _
try:
    from xml.etree import cElementTree as tree
except ImportError:
    import elementtree as tree

class __BASE__(object):
    """
    """
    def __init__(self, data, *args, **kws):
        self.__treedata = data
        self._args = args
        self._kws = kws

        children = self.__treedata.getchildren()
        if children:
            for c in children:
                if c.tag in self:
                    if not isinstance(getattr(self, c.tag), list):
                        tmp = getattr(self, c.tag)
                        setattr(self, c.tag, [tmp, _GetObj(c.tag, c)])
                    else:
                        getattr(self, c.tag).append(_GetObj(c.tag, c))
                else:
                    setattr(self, c.tag, _GetObj(c.tag, c))

        if self.__treedata.attrib:
            for a in self.__treedata.attrib:
                setattr(self, a, self.__treedata.get(a))

        if self.__treedata.text:
            self.text = self.__treedata.text

    def __repr__(self):
        """
        """
        return '<%s at %#x>' % (self.__class__.__name__, _.id(self))

    def __str__(self):
        """
        """
        return tree.tostring(self.__treedata)

    def __len__(self):
        """
        """
        return len(self.__treedata.getchildren())
    
    def __contains__(self, attr):
        """
        """
        return bool(hasattr(self, attr))

    def __iter__(self):
        """
        """
        return (v for k, v in self.__dict__.iteritems() 
                if not k.startswith('_'))
    
    def GetElementData(self):
        """
        """
        return self.__treedata


class ContentParser(object):
    """
    """
    def __init__(self, content, category):
        """
        """
        self._content = content
        self._category = category

    def objectify(self):
        """
        """
        feed = None
        try:
            feed = tree.fromstring(self._content)
        except Exception: pass
        if not feed: return
        return self._objectify(feed)

    def _objectify(self, feed):
        """
        """
        return _GetObj(self._category, feed)


def _GetObj(tagname, src):
    """
    """
    try:
        return globals()[tagname](src)
    except KeyError:
        exec 'class %s(__BASE__): pass' % tagname in globals()
        return globals()[tagname](src)
