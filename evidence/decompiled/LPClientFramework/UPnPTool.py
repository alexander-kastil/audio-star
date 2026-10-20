# Source Generated with Decompyle++
# File: UPnPTool.pyc (Python 3.9)

import requests
import html
from xml.sax.saxutils import escape
from bs4 import BeautifulSoup
from LPClientFramework.LPUtility import logger

def upnpPost(url, service, method, inParams, outParams, timeout = (15,)):
    serviceStr = 'urn:schemas-upnp-org:service:%s' % service
    if service == 'PlayQueue:1':
        serviceStr = 'urn:schemas-wiimu-com:service:%s' % service
    headers = {
        'Content-Type': 'text/xml; charset="utf-8"',
        'SOAPACTION': '"%s#%s"' % (serviceStr, method) }
    paramXML = ''
    for key, value in inParams.items():
        if type(value) != str:
            value = str(value)
        paramXML += '<%s>%s</%s>' % (key, escape(value), key)
    data = '<?xml version="1.0" encoding="utf-8"?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:%s xmlns:u="%s">%s</u:%s></s:Body></s:Envelope>' % (method, serviceStr, paramXML, method)
# WARNING: Decompyle incomplete

if __name__ == '__main__':
    print(upnpPost('http://192.168.50.64:59152/upnp/control/rendercontrol1', 'RenderingControl:1', 'GetChannel', {
        'InstanceID': '0',
        'Channel': 'Master' }, [
        'CurrentChannel']))
