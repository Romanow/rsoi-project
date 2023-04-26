import requests
from requests.auth import HTTPBasicAuth

url = 'auth.kurush7.cloud.okteto.net' #'localhost:5001'
dummy_client_id = 'pRiDvVWqbMdVcqUcubD0Y54V'
dummy_client_secret = 'tMWy9xDK6CaCe6LfqpO3BIqkjVgm8eEUnMLAdHaV5IO32Riu'
login = 'dummy'
password = 'dummy'

def create_guest_token():
    # step 1 - get code
    s = requests.Session()
    resp = s.request('POST', f'http://{url}/login', data={'login': login, 'password': password})
    if resp.status_code != 200:
        return 'failed to login', 500

    params = {
        'client_id': dummy_client_id,
        'response_type': 'code',
        'scope': 'openid'
    }

    resp = s.request('POST', f'http://{url}/oauth/authorize', params=params, data={'confirm': 'on'})
    if resp.status_code != 200:
        return 'failed to get code', 500

    location = resp.url
    idx = location.find('code=')
    code = location[idx+5:]

    resp = s.request('POST', f'http://{url}/oauth/token', data={'grant_type': 'authorization_code', 'code': code},
                     auth=HTTPBasicAuth(dummy_client_id, dummy_client_secret))
    if resp.status_code != 200:
        return 'failed to get token', 500
    data = resp.json()
    return data['id_token']

if __name__ == '__main__':
    token = create_guest_token()
    print('id token:\n\n')
    print(token)
    with open('dummy_token.txt', 'w') as f:
        f.write(token)