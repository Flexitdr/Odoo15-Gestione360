# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


class Request(object):

    """Generic request object."""

    _fields = None  # List of field names
    _params = None  # value of the fields
    _endpoint = None

    _url_endpoints = {
        'soap': '/POSWebServices/SOAP/default.asmx',
        'json': '/POSWebServices/JSON/default.aspx?{endpoint}',
        'http': '/POSWebServices/HTTP/default.aspx?{endpoint}'
    }

    def __init__(self, mode, **kwargs):
        if mode not in self._url_endpoints.keys():
            raise ValueError('Not a valid mode. Must be one of: [%s]'
                             % ', '.join(self._url_endpoints.keys()))

        self.mode = mode
        self._params = {}

        for param in kwargs:
            if param not in (self._fields or []):
                _logger.warning('Unknown parameter %s', param)
                continue

            self._params[param] = kwargs[param]

    def get_params(self):
        """Return a dict with the resquest params."""
        return {key: str(self._params[key]) for key in self._params}

    def endpoint(self, base_url):
        return '%s/%s' % (base_url, self._url_endpoints[self.mode].format(
            endpoint=self._endpoint))


class SaleRequest(Request):

    """Sale request record.

    The in the API response all fields are strings.

    Campo             Descripción
    ---------------------------------------------------------------------------
    Amount            Monto total de la transacción.
    ITBIS             Monto total de impuestos.
    OrderNumber       Número de transacción.
    MerchantId        ID del comercio. (Provisto por AZUL)
    Installment       Cuotas de la transacción. Esto solo aplica para tarjetas
                      las cuales posean esta funcionalidad. Valores: 0 ~ 99
    UseMultiMessaging Permite habilitar la funcionalidad de otorgar descuentos
                      (Promociones) al cliente. Valores: 1 (True), 0 (False)
    PromoData         Permite definir el descuento que desea aplicar al
                      tarjetahabiente utilizando el BIN de la tarjeta utilizada
                      en la transacción. Se pueden definir las reglas de dos
                      maneras:

                      * Porcentaje por BIN: Se define el BIN de la tarjeta
                      a aplicar el descuento seguido del porcentaje de
                      descuento separado por dos puntos (:).
                      Ejemplo: <PromoData>540011:12%</PromoData>
                      En este ejemplo cuando se utilice una tarjeta que inicie
                      con el BIN 540011 se le aplicara un 12% de descuento al
                      monto total.

                      * Monto por BIN: Se define el BIN de la tarjeta a aplicar
                      el descuento seguido del monto fijo de descuento separado
                      por dos puntos (:)
                      Ejemplo: <PromoData>401200:100</PromoData>
                      En este ejemplo cuando se utilice una tarjeta que inicie
                      con el BIN 401200 se le aplicará al monto total un
                      descuento de 100 pesos.


    Response example for JSON:
        {
            "Amount":"1.00",
            "Installment":"0",
            "Itbis":"1.00",
            "MerchantId":"39271010043",
            "OrderNumber":"100926",
            "PromoData":"",
            "UseMultiMessaging":"1"
        }
    """

    _endpoint = 'Sale'
    _fields = [
        'Amount', 'ITBIS', 'OrderNumber', 'MerchantId',
        'Installment', 'UseMultiMessaging', 'PromoData'
    ]


class RefundRequest(Request):

    """Refund request record.

    The in the API response all fields are strings.

    Campo             Descripción
    ---------------------------------------------------------------------------
    Amount            Monto total de la transacción.
    ITBIS             Monto total de impuestos.
    OrderNumber       Número de transacción.
    MerchantId        ID del comercio. (Provisto por AZUL)
    """

    _endpoint = 'Refund'
    _fields = ['Amount', 'ITBIS', 'OrderNumber', 'MerchantId']


class CancellationRequest(Request):
    """Request for cancellation.

    Campo             Descripción
    ---------------------------------------------------------------------------
    Amount              Monto total de la transacción.
    ITBIS               Monto total de impuestos.
    OrderNumber         Numero de transacción.
    MerchantId          ID del comercio. (Provisto por AZUL)
    AuthorizationNumber Número de la autorización obtenida en la transacción
                        que se desea anular.
    """

    _endpoint = 'SaleCancellation'
    _fields = [
        'Amount', 'ITBIS', 'OrderNumber', 'MerchantId',
        'AuthorizationNumber'
    ]


class MobilePaymentRequest(Request):

    """Mobile payment request record.

    The in the API response all fields are strings.

    Campo             Descripción
    ---------------------------------------------------------------------------
    Amount            Monto total de la transacción.
    ITBIS             Monto total de impuestos.
    OrderNumber       Número de transacción.
    MerchantId        ID del comercio. (Provisto por AZUL)
    Installment       Cuotas de la transacción. Esto solo aplica para tarjetas
                      las cuales posean esta funcionalidad. Valores: 0 ~ 99
    UseMultiMessaging Permite habilitar la funcionalidad de otorgar descuentos
                      (Promociones) al cliente. Valores: 1 (True), 0 (False)
    """

    _endpoint = 'MobilePayment'
    _fields = [
        'Amount', 'ITBIS', 'OrderNumber', 'MerchantId',
        'Installment', 'UseMultiMessaging'
    ]
