import requests
import hmac
import json
import time
from urllib.parse import urlencode

URL = 'https://www.bitmex.com'
API_KEY = 'YOUR_API_KEY_HERE'
API_SECRET = 'YOUR_API_SECRET_HERE'


def query(request_type, api_method, params=None):
    """ Make a request to trading exchange.

    :param request_type: type of the request - get, post, put or delete
    :param api_method: target api method from BitMEX API specification
    :param params: additional parameters of the request
    :return: text from requests.Response object
    """

    try:
        api_method = '/api/v1' + api_method
        url = URL + api_method
        try:
            params = urlencode(params)
        except:
            params = None

        # building a request and signature
        headers = {'user-agent': 'my-python-connector'}
        expires = str(int(round(time.time()) + 3600))
        if str(request_type).lower() == "get":
            post = ''
            if params is not None:
                api_method = api_method + "?" + params
        else:
            post = params
        message = bytes(request_type + api_method + expires + post, 'utf-8')
        signature = hmac.new(bytes(API_SECRET, 'utf-8'), message, 'sha256').hexdigest()
        headers['api-expires'] = expires
        headers['api-key'] = API_KEY
        headers['api-signature'] = signature
        headers['Content-type'] = "application/x-www-form-urlencoded"
        print("request: " + request_type + ' ' + url + '?' + api_method)

        response = None
        if str(request_type).lower() == "get":
            response = requests.get(url, headers=headers, params=params)
        if str(request_type).lower() == "post":
            response = requests.post(url, headers=headers, data=params)
        if str(request_type).lower() == "put":
            response = requests.put(url, headers=headers, data=params)
        if str(request_type).lower() == "delete":
            response = requests.delete(url, headers=headers, data=params)
        print("response: " + response.text)

        # handling of response headers. Printing additional info about RateLimit
        try:
            limit = response.headers["X-RateLimit-Limit"]
            remaining = response.headers["X-RateLimit-Remaining"]
            api_load = round(100.0 - (100.0 / float(limit)) * float(remaining), 2)
            print('api load: ' + str(api_load) + '%')
        except Exception as e:
            print(str(e))

        # HTTP errors handling
        if response.status_code != requests.codes.ok:
            try:
                res_er = json.loads(response.text)
                print(res_er['error']['message'])
            except Exception as e:
                print('unexpected internal error: ' + str(e))

        return response.text
    except Exception as e:
        print('[Exception] query: ' + str(e))
    return None


# test method for get bars
def get_bars(symbol='XRPUSDT', time_frame='1h', start=None, count=1000):
    params = {
        'symbol': symbol,
        'binSize': time_frame,
        'partial': True,
        'count': count,
        'columns': "timestamp, open, high, low, close, volume"
    }
    if start is not None:
        params['start'] = start
    response = query('GET', '/trade/bucketed', params)
    if response is not None:
        return json.loads(response)


# test method for get wallet assets
def get_wallet_assets():
    response = query('GET', '/wallet/assets')
    if response is not None:
        return json.loads(response)


print('Request to /trade/bucketed:')
print(get_bars())
print('Request to /wallet/assets:')
print(get_wallet_assets())
