from enum import Enum

from qr_server.request_sending import *


class Service(Enum):
    AUTH = 1
    SEARCH = 2
    SCOUT = 3
    FILE = 4

SERVICE_NAMES = {
    Service.AUTH: 'auth',
    Service.SEARCH: 'search',
    Service.SCOUT: 'scout',
    Service.FILE: 'file',
}

# def get_book(address: QRAddress, uid: str, auth_headers: dict):
#     resp = send_request_supress(address, f'api/v1/books/{uid}', request=QRRequest(headers=auth_headers))
#     if resp.status_code != 200:
#         return None
#     return resp.get_json()
#
#
# def get_library(address: QRAddress, uid: str, auth_headers):
#     resp = send_request_supress(address, f'api/v1/libraries/{uid}', request=QRRequest(headers=auth_headers))
#     if resp.status_code != 200:
#         return None
#     return resp.get_json()


def send_request_supress(address: QRAddress, url: str, method='GET', request: QRRequest = None):
    # sends error response if smth went wrong instead of an exception
    try:
        return send_request(address, url, method, request)
    except Exception as e:
        return QRResponse(False, 500, str(e), bytes())


def send_request_raw_supress(address: QRAddress, url: str, method='GET', request: QRRequest = None):
    try:
        if request is None:
            request = QRRequest(None, None, None)

        resp = requests.request(method, address.get_full_url(url), **request.get_args())
        return resp
    except Exception as e:
        return QRResponse(False, 500, str(e), bytes())


def knock_service(address: QRAddress, throw_exception: bool = False):
    try:
        resp = requests.request('GET', address.get_full_url('manage/health'))
        ok = resp.status_code == 200
    except Exception:
        ok = False
    if throw_exception and not ok:
        raise Exception('knock service: failed')
    return ok