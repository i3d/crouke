#!/usr/bin/env python

# system library
import urllib

# temporary for development environment
# should be configured to use python-support pth in release
import sys
sys.path.append('..')

# Crouke library
from config import settings
from config import texts as _
from utils import LogInToken
import excepts

# the server list will be read from file
import client

_METHODS = {'CATEGORY' : '/V1/CATEGORIES/',
            'LIST' : '/V1/LIST/%s/%s/%s',
            'CONTENT' : '/V1/GET/%s/',
            'VOTE' : '/V1/VOTE/%s/%s' }
_SORTMODE = ['new', 'alpha', 'high', 'down' ]
_VOTES = ['good', 'bad']
_CATEGORY_SEPARATER = 'x'


class Crouke(object):
    """
    """
    def __init__(self, user=None, password=None, site=None):
        """
        """
        self._user = user
        self._password = password
        if site and site not in settings.SITES:
            self.AddNewSite(site)
        self._site = site
    
    def ProgrammaticLogin(self):
        """Do Programmatic login test.
        """
        if not self._user or not self._password:
            try:
                login = LogInToken()
                login.Load()
            except excepts.LoadLoginCacheError:
                return _.load_failed
            else:
                self._user, self._password = login.GetToken()
        
        # just pick the first site to try login since these sites
        # are all share the login info.
        cat = client.CroukeClient(self._user, self._password,
                                  settings.SITES[0]).Get(
                                  _METHODS['CATEGORY'])
        if not cat:
            return _.auth_failed

    def AddNewSite(self, site):
        """
        """
        settings.SITES.append(site)

    def GetCategory(self):
        """
        """
        # a list of two-element tuple ('id', 'name')
        clist = []
        cat = client.CroukeClient(
            self._user, self._password, self._site).Get(_METHODS['CATEGORY'])
        if cat and cat.status.text == 'ok':
            clist = [(i.id, i.text) for i in cat.data.category]
            #clist.sort(key=lambda k: k[1])
        return clist

    def GetListId(self, cat_id_list, sortmode=_SORTMODE[0], page=0):
        """
        """
        content_list_id = []
        cats = ''.join([i + _CATEGORY_SEPARATER
                        for i in cat_id_list]).strip(_CATEGORY_SEPARATER)
        uri = _METHODS['LIST'] % (cats, sortmode, page)
        lst = client.CroukeClient(self._user, self._password,
                                  self._site).Get(uri)
        if lst and lst.status.text == 'ok':
            content_list_id = [(i.id.text, i.changed.text, i.name.text,
                                i.score.text, i.downloads.text) 
                               for i in lst.data.entry]
            if sortmode == _SORTMODE[0]:
                content_list_id.sort(key=lambda i: long(i[1]))
            elif sortmode == _SORTMODE[1]:
                content_list.sort(key=lambda i: i[2])
            elif sortmode == _SORTMODE[2]:
                content_list.sort(key=lambda i: int(i[3]), reverse=True)
            elif sortmode == _SORTMODE[3]:
                content_list.sort(key=lambda i: int(i[4]), reverse=True)
        return [i[0] for i in content_list_id]

    def GetContent(self, content_id):
        """
        """
        # a list of content elements in sequence:
        # downloadlink, description, downloadsize, homepage, changelog
        # license, language, preview1, preview2, preview3, smallpreviewpic1
        content = {}
        cont = client.CroukeClient(self._user, self._password,
                                   self._site).Get(
                                    _METHODS['CONTENT'] % content_id)
                                    
        if cont and cont.status.text == 'ok':
            content = content.fromkeys(client.GetElementTagFromData(cont.data),
                                       None)
            for key in content:
                if 'text' in getattr(cont.data, key):
                    content[key] = unicode(
                        urllib.unquote(getattr(cont.data, key).text), 'utf-8',
                        'ignore')
        return content

    def Vote(self, content_id, vote):
        """
        """
        vot = client.CroukeClient(self._user, self._password,
                                  self._site).Get(_METHODS['VOTE'] %
                                                       (content_id, vote))
        if vot: return vot.status.text

    def GetAll(self, sortmode=_SORTMODE[0], page=0):
        """The default main page is to point at all category first page"""
        cates = self.GetCategory()
        clists = self.GetListId([i[0] for i in cates], sortmode=sortmode,
                                page=page)
        contents = [self.GetContent(i) for i in clists]
        return ([i[1] for i in cates], contents)
