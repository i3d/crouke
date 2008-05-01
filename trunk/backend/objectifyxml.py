#!/usr/bin/env python

"""Provide objectify algorithm to convert a xml data into a python object.
"""

import __builtin__ as _
try:
    from xml.etree import cElementTree as tree
except ImportError:
    import elementtree as tree

class __BASE__(object):
    """A base meta class where all elements will be built from.
    """

    def __init__(self, data, *args, **kws):
        """Constructor to init the object.

        Args:
            data: the xml element data.
            args: extra args.
            kws: extra kws.
        """
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
        """Return the object representation form.
        """
        return '<%s at %#x>' % (self.__class__.__name__, _.id(self))

    def __str__(self):
        """Return the object string form.
        """
        return tree.tostring(self.__treedata)

    def __len__(self):
        """Return the number of child elements in a given element.
        """
        return len(self.__treedata.getchildren())
    
    def __contains__(self, attr):
        """Boolean whether an attribute is in this object.
        """
        return bool(hasattr(self, attr))

    def __iter__(self):
        """Construct an iterator for this object.
        """
        return (v for k, v in self.__dict__.iteritems() 
                if not k.startswith('_'))
    
    def GetElementData(self):
        """Return the underlie elementtree object.
        """
        return self.__treedata


class ContentParser(object):
    """The content data parser class.
    """

    def __init__(self, content, category):
        """Constructor to init the object.

        Args:
            content: the content xml string.
            category: the category type of this content.
        """
        self._content = content
        self._category = category

    def objectify(self):
        """Convert the xml string to a python object.
        
        The actual implementation is done by _objectify.
        """
        element = tree.fromstring(self._content)
        return self._objectify(element)

    def _objectify(self, element):
        """Do the object convertion.

        Args:
            element: an elementtree element.
        """
        return _GetObj(self._category, element)


def _GetObj(tagname, src):
    """Construct a python object by giving the element tree object.

    Args:
        tagname: the tagname of the element. Used to 
                 form the object's attribute.
        src: the elementtree object.
    """
    try:
        return globals()[tagname](src)
    except KeyError:
        exec 'class %s(__BASE__): pass' % tagname in globals()
        return globals()[tagname](src)
