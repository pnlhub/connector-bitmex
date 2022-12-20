import requests
import hmac
import json
import time
from urllib.parse import urlencode

URL = 'https://www.bitmex.com'
API_KEY = 'VX_f9zZEG6Nst9azbwqVOj8M'
API_SECRET = 'DQLZZrDzXI_7PzGPB8igUyl8hSPmRr8b-CbIKZjEvBMO4j3l'

def query(method, function, params=None):
    try:
        function = '/api/v1' + function
        url = URL + function
        try:
            params = urlencode(params)
        except:
            params = None

        # Формирование запроса и подписи
        headers = {'user-agent': 'my-python-connector'}
        expires = str(int(round(time.time()) + 3600))  # set expires one hour in the future
        if str(method).lower() == "get":
            post = ''
            if params is not None:
                function = function + "?" + params
        else:
            post = params
        message = bytes(method + function + expires + post, 'utf-8')
        signature = hmac.new(bytes(API_SECRET, 'utf-8'), message, 'sha256').hexdigest()
        headers['api-expires'] = expires
        headers['api-key'] = API_KEY
        headers['api-signature'] = signature
        headers['Content-type'] = "application/x-www-form-urlencoded"
        print("request: " + method + ' ' + url + '?' + str(params))

        response = None
        if str(method).lower() == "get":
            response = requests.get(url, headers=headers, params=params)
        if str(method).lower() == "post":
            response = requests.post(url, headers=headers, data=params)
        if str(method).lower() == "put":
            response = requests.put(url, headers=headers, data=params)
        if str(method).lower() == "delete":
            response = requests.delete(url, headers=headers, data=params)
        print("response: " + response.text)

        # обработка хедеров респонса. Вывод дополнительной информации о RateLimit
        try:
            limit = response.headers["X-RateLimit-Limit"]
            remaining = response.headers["X-RateLimit-Remaining"]
            api_load = round(100.0 - (100.0 / float(limit)) * float(remaining), 2)
            print('api load: ' + str(api_load) + '%')
        except Exception as eh:
            pass

        # обработка http ошибок
        if response.status_code != requests.codes.ok:
            try:
                res_er = json.loads(response.text)
                info = res_er['error']['message']
            except Exception as e:
                info = 'unexpected internal error: ' + str(e)

        return response.text
    except Exception as e:
        print('[Exception] query: ' + str(e))
    return None


def get_bars(symbol='XRPUSDT', time_frame='1h', start=None, count=1000):
    params = {'symbol': symbol, 'binSize': time_frame, 'partial': True,
            'count': count,
            'columns': "timestamp, open, high, low, close, volume"}
    if start is not None:
        params['start'] = start
    response = query('GET', '/trade/bucketed', params)
    if response is not None:
        return json.loads(response)
    pass


def get_wallet_assets():
    response = query('GET', '/wallet/assets')
    if response is not None:
        return json.loads(response)
    return None

print('Делаем запрос /wallet/assets:')
get_wallet_assets()
