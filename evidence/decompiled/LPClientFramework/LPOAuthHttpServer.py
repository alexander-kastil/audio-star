# Source Generated with Decompyle++
# File: LPOAuthHttpServer.pyc (Python 3.9)

import cherrypy
import LPGlobalUI
from LPClientFramework import LPUtility
from LPClientFramework.LPPlayList.LPPlayList import LPPlayListSource
from LPClientFramework.LPUtility import logger

class OAuthServerPage:
    
    def index(self):
        return 'WiiM Home OAuth Service'

    index = cherrypy.expose(index)
    
    def qobuz(self, *args, **params):
        if args and args[0] != 'wiimhome':
            return None
        code = None.getExchangeCode(params)
        if code:
            notify = {
                'exchange_code': code,
                'source': LPPlayListSource.Qobuz.value }
            self.sendOAuthCodeGotNotify(LPGlobalUI.currentDevice, notify)
            return self.build_callback_page()

    qobuz = cherrypy.expose(qobuz)
    
    def tidal(self, *args, **params):
        '''
        处理 TIDAL OAuth redirect 回调。

        :param args: URL 路径参数，只接受 /tidal/wiimhome。
        :param params: query 参数。
        :return: 授权完成页面或错误页面。
        '''
        if args and args[0] != 'wiimhome':
            return None
        error = params.get('error', None) if None else None
        if error:
            logger.info('[TIDAL] OAuth callback returned error=%s', error)
            return self.build_callback_page('Authorization cancelled, return to WiiM Home.')
        state = params.get('state', None) if None else None
        if state and state not in ('login_state', 'pc'):
            logger.warning('[TIDAL] OAuth callback ignored because state mismatch: %s', state)
            return self.build_callback_page('Authorization state mismatch, return to WiiM Home and try again.')
        code = None.getExchangeCode(params)
        if code:
            notify = {
                'exchange_code': code,
                'source': LPPlayListSource.Tidal.value }
            self.sendOAuthCodeGotNotify(LPGlobalUI.currentDevice, notify)
            return self.build_callback_page()

    tidal = cherrypy.expose(tidal)
    
    def getExchangeCode(self, params):
        if params:
            return params.get('code', None)

    
    def sendOAuthCodeGotNotify(self, device, notify):
        LPUtility.postNotification('OAuthCodeChanged', {
            'device': device,
            'notify': notify })

    
    def build_callback_page(self, message = ('Authorization successful, starting WiiM Home...',)):
        '''
        构建 OAuth 回调完成页并唤起 App。

        :param message: 页面提示文案。
        :return: HTML 字符串。
        '''
        logger.debug('[build_callback_page]')
        html = '\n        <html>\n        <body>\n            <h2>%s</h2>\n            <p>If not redirected automatically, click <a id="link" href="wiim://active">here</a> or return to WiiM Home manually.</p>\n            <script>\n                setTimeout(() => {\n                    document.getElementById("link").click();\n                }, 1000);\n            </script>\n        </body>\n        </html>\n        ' % message
        cherrypy.response.headers['Content-Type'] = 'text/html'
        return html


