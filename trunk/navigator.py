"""Implement navigation subsystem for Crouke.
"""

class Navigator(object):
    """A navigation object responses to navigation key strocks.
    """
    # store stacks of pages.
    _cache = {}

    @classmethod
    def CleanCache(cls):
        cls._cache = {}

    def __init__(self, parent):
        """Construct the object.

        Args:
            parent: parent page.
        """
        if not self._cache:
            self._pos = -1
            self._on_site = None
            self._parent = parent
            self._InitCache(parent)

    def _InitCache(self, widget):
        """Build the data structure for all sites.
        """
        for child in widget.children():
            self._cache[child.get_name.replace('_button', '')] = []

    def Store(self, site, page_obj):
        if page_obj not in self._cache[site]:
            self._cache[site].append(page_obj)
            return True
        return False

    def GetPage(self):
        if not self._on_site or self._pos < 0: return
        return self._cache.get(self._on_site)[self._pos]

    def SetPos(self, pos):
        self._pos = pos

    def GetPos(self):
        return self._pos

    def SetSite(self, site):
        if site in self._cache:
            self._on_site = site
            return True
        return False

    def GetOnSite(self):
        return self._on_site






