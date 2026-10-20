# Source Generated with Decompyle++
# File: LPUPnPHttpServer.pyc (Python 3.9)

from PyQt6.QtWidgets import QApplication
import codecs
from bs4 import BeautifulSoup
from xml.sax.saxutils import escape
import re
from beets import util
import cherrypy
import sys
import platform
import LPGlobalUI
from LPClientFramework import LPUtility, LPBeetsWrapper
from LPClientFramework.LPBeetsWrapper import UPNP_DIRID_PLAYLISTROOT
from LPClientFramework.LPUtility import logger
SOAP_PARSER = 'xml'
SERVER_STRING = '%s/%s UPnP/1.0 DLNADOC/1.50 WiiMHome/%s' % (platform.system(), platform.release(), QApplication.applicationVersion())
from cherrypy.lib.caching import MemoryCache
cache = MemoryCache()

class UPnPServerPage:
    
    def index(self):
        return 'WiiM Home UPnP Service'

    index = cherrypy.expose(index)
    
    def DeviceDescription_xml(self):
        with codecs.open('%s/LPUPnPServer.xml' % LPUtility.appLocalDataPath(), 'r', 'utf-8', 'ignore', **('errors',)) as configFile:
            data = configFile.read()
            upnpDict = LPUtility.objectForUserconfig('upnpserver')
            data = data % (upnpDict.get('name', ''), QApplication.applicationVersion(), 'uuid:%s' % LPUtility.pcUUID())
            size = sys.getsizeof(data)
            cache.put(data, size)
            None(None, None, None)
        with None:
            if not None:
                pass
        cherrypy.response.headers['Content-Type'] = 'application/xml'
        return data.encode()

    DeviceDescription_xml = cherrypy.expose(DeviceDescription_xml)
    
    def images(self, imagename):
        if imagename == 'ico.png':
            data = cache.get()
            if data is None:
                with open(LPGlobalUI.imagePath('ico.png'), 'rb') as f:
                    data = f.read()
                    size = sys.getsizeof(data)
                    cache.put(data, size)
                    None(None, None, None)
                with None:
                    if not None:
                        pass
            cherrypy.response.headers['Content-Type'] = 'image/png'
            return data
        raise cherrypy.HTTPError(404, f'''File {imagename}.png not found''')

    images = cherrypy.expose(images)
    
    class ContentDirectory:
        
        def index(self):
            return 'WiiM Home UPnP ContentDirectory Service'

        index = cherrypy.expose(index)
        
        def scpd_xml(self):
            data = cache.get()
            if data is None:
                with codecs.open('%s/LPContentDirectory.xml' % LPUtility.appLocalDataPath(), 'r', 'utf-8', 'ignore', **('errors',)) as configFile:
                    data = configFile.read()
                    size = sys.getsizeof(data)
                    cache.put(data, size)
                    None(None, None, None)
                with None:
                    if not None:
                        pass
            cherrypy.response.headers['Content-Type'] = 'application/xml'
            return data.encode()

        scpd_xml = cherrypy.expose(scpd_xml)
        
        def control_xml(self, **params):
            headers = cherrypy.request.headers
        # WARNING: Decompyle incomplete

        control_xml = cherrypy.expose(control_xml)
        
        def dealWithBrowse(self, requestBody):
            pass
        # WARNING: Decompyle incomplete

        
        def dealWithSearch(self, requestBody):
            emptyBody = '<?xml version="1.0" encoding="utf-8"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><u:SearchResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1"><Result></Result><NumberReturned>0</NumberReturned><TotalMatches>0</TotalMatches><UpdateID>0</UpdateID></u:SearchResponse></s:Body></s:Envelope>'
        # WARNING: Decompyle incomplete

        
        def generateErrorXML(self, code, reason):
            return '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body><s:Fault><faultcode>s:Client</faultcode><faultstring>UPnPError</faultstring><detail><UPnPError xmlns="urn:schemas-upnp-org:control-1-0"><errorCode>%d</errorCode><errorDescription>%s</errorDescription></UPnPError></detail></s:Fault></s:Body></s:Envelope>' % (code, reason)

        
        def generateBodyXML(self, rows):
            localIP = LPUtility.fetchLocalIP()
            bodyStr = ''
        # WARNING: Decompyle incomplete

        
        def parseSortCriteria(self, sortCriteria):
            order = ''
            error = 0
            if not sortCriteria:
                return (None, error)
            items = None.split(',')
            order += 'ORDER BY '
            title_sorted = False
            for i, item in enumerate(items):
                reverse = False
                if i:
                    order += ', '
                if item.startswith('+'):
                    item = item[1:]
                elif item.startswith('-'):
                    reverse = True
                    item = item[1:]
                else:
                    logger.warning('LPUPnPServer parseSortCriteria No order specified %s' % item)
                    error = -1
                    return (None, error)
                if None.lower() == 'upnp:class':
                    order += 'u.upnp_class'
                elif item.lower() == 'dc:title':
                    order += 'i.title'
                    title_sorted = True
                elif item.lower() == 'dc:date':
                    order += 'u.upnp_date'
                elif item.lower() == 'upnp:originaltracknumber':
                    order += 'i.disk, i.track'
                elif item.lower() == 'upnp:album':
                    order += 'i.album'
                else:
                    logger.warning('LPUPnPServer parseSortCriteria Unhandled SortCriteria %s' % items)
                    error = -1
                    if i:
                        order = order[:-2]
                    return (None, error)
                if None:
                    order += ' DESC'
                    continue
                    if not items:
                        return (None, error)
                    if not None:
                        order += ', title ASC'
            return (order, error)


    contentdirectory = ContentDirectory()

