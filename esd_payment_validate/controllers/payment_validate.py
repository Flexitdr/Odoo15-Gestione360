import requests

import posixpath
from odoo.http import request
from ..auth import auth


def read_azul_transaction(as_dict=True):

    try:

        url = "https://ftp1.azul.com.do/Salida/"

        response = requests.get(url, auth=(auth.Auth['User'], auth.Auth['Password']))

        response_file = response.text.split()[24]

        url_to_join = response_file.replace('</a>', '').replace('<br>', '')

        final_url_to_join = url_to_join.split('>')

        a = final_url_to_join[1]

        path = posixpath.join(url, a)

        final_response = requests.get(path, auth=(auth.Auth['User'], auth.Auth['Password']))

        try:
            open("tmp/transactions.txt", "wb").write(final_response.content)

        except Exception as e:

            return {'error': True, 'message': repr(e)}

        url_file = 'tmp/transactions.txt'

        f = open(url_file, 'r')

        result = f.read().split('|')

        res = result[6:]

        list_string = []

        list_of_list = []

        for line in res:

            if 'ResponseMessage' not in line:
                list_string.append(line)
            else:
                list_string.append(line)
                list_of_list.append(list_string)
                list_string = []

        list_dict = []

        for line_list in list_of_list:

            if as_dict:
                dict(zip([
                    'MID',
                    'SubscriptionId',
                    'Group',
                    'Name',
                    'IdentType',
                    'IdentNum',
                    'Contract',
                    'CardNumber',
                    'Currency',
                    'Amount',
                    'Tax',
                    'TransactionDate',
                    'TransactionType',
                    'Approved',
                    'AuthorizationNumber',
                    'RRN',
                    'ResponseCode',
                    'ResponseMessage'

                ], line_list))

                key_dict = [item.split(':', 1)[0] for item in line_list]

                value_dict = [item.split(':', 1)[1] for item in line_list]

                dict_final = dict(map(lambda i, j: (i, j), key_dict, value_dict))

                if dict_final['Approved'] != 'N':

                    request.env['azul.books'].sudo().create({

                        'mid': dict_final['MID'],
                        'subscription_id': dict_final['SubscriptionId'],
                        'group': dict_final['Group'],
                        'name': dict_final['Name'],
                        'ident_type': dict_final['IdentType'],
                        'ident_num': dict_final['IdentNum'],
                        'contract': dict_final['Contract'],
                        'card_number': dict_final['CardNumber'],
                        'currency': dict_final['Currency'],
                        'amount': float(dict_final['Amount'].replace(',', '')),
                        'tax': dict_final['Tax'],
                        'transaction_date': dict_final['TransactionDate'],
                        'transaction_type': dict_final['TransactionType'],
                        'approved': dict_final['Approved'],
                        'authorization_number': dict_final['AuthorizationNumber'],
                        'rrn': dict_final['RRN'],
                        'response_code': dict_final['ResponseCode'],
                        'response_message': dict_final['ResponseMessage']

                    })

                    list_dict.append(dict_final)

        return list_dict

    except Exception as e:

        return {'error': True, 'message': repr(e)}


def clean_text_file(url):
    try:
        ptr = 1

        for line in url:

            if ptr != 0:
                url.write(line)
            ptr += 1

    except Exception as e:

        return {'error': True, 'message': repr(e)}




