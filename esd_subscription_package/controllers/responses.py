# -*- coding: utf-8 -*-

import json
import logging

_logger = logging.getLogger(__name__)


class Response(object):
    _fields = None  # List of field names
    _params = None  # value of the fields

    def __init__(self, **kwargs):
        self._params = {}

        for param in kwargs:
            if param not in (self._fields or []):
                _logger.warning('Unknown parameter %s', param)
                continue

            self._params[param] = kwargs[param]

    def get_params(self):
        """Return a dict with the resquest params."""
        return {key: str(self._params[key]) for key in self._params}

    @classmethod
    def fromString(cls, string):
        params = json.loads(string)

        return cls(**params)


class SaleResponse(Response):

    """Sale response record.

    Campo             Descripción
    ---------------------------------------------------------------------------
    DateTime         Fecha y hora de la transacción en formato YYYYMMDDHHMMSS
    ResponseCode     Código de respuesta de la transacción. (1[49] == OK)
    ResponseMessage  Descripción del código de respuesta recibido.
    ErrorDescription Descripción del error recibido.
    ReceiptMerchant  Voucher del comercio
    ReceiptClient    Voucher del cliente
    QuickPayment     Indica si se utilizó la modalidad de Pago Rápido.
    RequireSignature Indica si se firmó digitalmente la transacción o si
                     requiere firma física en el voucher.
    SignatureData    Firma digital del cliente en formato Base64.
    OrderNumber      Número de transacción.
    ResponseFields   Arreglo dinámico con todos los campos antes mencionados,
                     más información complementaria de la transacción.
    """

    _fields = [
        'DateTime', 'ResponseCode', 'ResponseMessage', 'ErrorDescription',
        'ReceiptMerchant', 'ReceiptClient', 'QuickPayment', 'RequireSignature',
        'SignatureData', 'OrderNumber', 'ResponseFields'
    ]


class RefundReponse(Response):

    """Refund response record.

    Campo             Descripción
    ---------------------------------------------------------------------------
    DateTime         Fecha y hora de la transacción en formato YYYYMMDDHHMMSS
    ResponseCode     Código de respuesta de la transacción. (1[49] == OK)
    ResponseMessage  Descripción del código de respuesta recibido.
    IsoCode          Código ISO de la respuesta.
    ErrorDescription Descripción del error recibido.
    ReceiptMerchant  Voucher del comercio
    ReceiptClient    Voucher del cliente
    SignatureData    Firma digital del cliente en formato Base64.
    RequireSignature Indica si se firmó digitalmente la transacción o si
                     requiere firma física en el voucher.
    QuickPayment     Indica si se utilizó la modalidad de Pago Rápido.
    OrderNumber      Número de transacción.
    ResponseFields   Arreglo dinámico con todos los campos antes mencionados,
                     más información complementaria de la transacción.
    """

    _fields = [
        'DateTime', 'ResponseCode', 'ResponseMessage', 'IsoCode',
        'ErrorDescription', 'ReceiptMerchant', 'ReceiptClient', 'QuickPayment',
        'RequireSignature', 'SignatureData', 'OrderNumber', 'ResponseFields'
    ]


class LastTransactionResponse(Response):

    """Search Last Transaction response.

    Campo             Descripción
    ---------------------------------------------------------------------------
    DateTime         Fecha y hora de la transacción en formato YYYYMMDDHHMMSS
    ResponseCode     Código de respuesta de la transacción. (1[49] == OK)
    ResponseMessage  Descripción del código de respuesta recibido.
    IsoCode          Código ISO de la respuesta.
    ErrorDescription Descripción del error recibido.
    ReceiptMerchant  Voucher del comercio
    """

    _fields = [
        'DateTime', 'ResponseCode', 'ResponseMessage', 'ErrorDescription',
        'ReceiptMerchant'
    ]
