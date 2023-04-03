# -*- coding: utf-8 -*-

"""
Azul REST API

TEST SETTINGS:
-------------
URL: https://pruebas.azul.com.do
MID: 39271010043
TID: 01290010
Auth1/Auth2: merit/merit
"""

import logging
import urllib
import urllib2
from esd_subscription_package.controllers.requests import SaleRequest
from esd_subscription_package.controllers.responses import SaleResponse


_logger = logging.getLogger(__name__)


class AzulRestApi(object):

    def __init__(self, url, mode, auth_user, auth_password, timeout=None):

        self.url = url
        self.mode = mode
        self.auth_user = auth_user
        self.auth_password = auth_password

        self.contentype = 'Content-Type: %s ' % (
            'text/xml' if mode == 'soap' else
            'application/json' if mode == 'json' else
            'application/x-www-form-urlencoded'
        )

        self.timeout = timeout or 160

        self.headers = {
            'Accept': '*/*',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        }

    def _json_request(self, request):
        headers = dict(self.headers)
        headers.update({
            'Content-Type': 'application/json; charset=utf-8',
            'Auth1': self.auth_user,
            'Auth2': self.auth_password
        })

        url = request.endpoint(self.url)

        data = urllib.urlencode(request.get_params())
        request = urllib2.Request(url=url, data=data, headers=headers)

        try:
            response = urllib2.urlopen(request, timeout=self.timeout)
            res = response.read()
        except urllib2.URLError as error:
            _logger.error(str(error))

            return False

        try:
            return SaleResponse.fromString(res)
        except ValueError:
            return None

    def _soap_request(self, request):
        raise NotImplementedError('Unsupported: soap')

    def _html_request(self, request):
        raise NotImplementedError('Not supported: html')

    def _make_request(self, request):
        if not hasattr(self, '_%s_request' % request.mode):
            raise ValueError('Not supported request mode: %s' % request.mode)

        return getattr(self, '_%s_request' % request.mode)(request)

    def initialization(self):
        pass

    def sale(self, sale_request):
        # type: (self, SaleRequest) -> SaleResponse
        if isinstance(sale_request, dict):
            sale_request = SaleRequest(self.mode, **sale_request)

        return self._make_request(sale_request)


if __name__ == '__main__':
    api = AzulRestApi('https://pruebas.azul.com.do', '39271010043', '01290010',
                      'merit', 'merit', 160)
