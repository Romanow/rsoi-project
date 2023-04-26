from flask import url_for
from flask import redirect as flask_redirect
from qr_server.Server import MethodResult, QRContext

from .dtos import *
from .utils import *
from .circuit_breaker import circuitBreaker, Service, ServiceUnavailableException
from common.jwt_validator import with_jwt_token, require_role


def make_proxy(proxy_name: str, service: Service, unpack_dto_cls, method='GET', url_updater=None,
               need_unpack=True, return_raw=False, redirect=False,
               require_roles=None, use_guest_token=False, extract_full_user=False,
               full_replace_url=None):
    """
    url_updater - converts url from local to service's url if needed (used mostly for the case of dynamic url with need of building full url)
    """
    @circuitBreaker.circuit([service], MethodResult(f'{SERVICE_NAMES[service]} service unavailable', 503))
    def wrapper(ctx: QRContext, **url_kwargs):
        full_url = url_for(proxy_name, **url_kwargs)
        if url_updater:
            full_url = url_updater(full_url)

        address = circuitBreaker.service_urls[service]

        if redirect:
            full_url = url_for(proxy_name, **url_kwargs, **ctx.params)
            if url_updater:
                full_url = url_updater(full_url)
            full_url = address.get_full_url(full_url)
            if full_replace_url is not None:
                idx = full_url.find('?')
                params = '' if idx == -1 else full_url[idx:]
                full_url = full_replace_url + params
            return flask_redirect(full_url, code=302)
            #return flask_redirect(address.get_full_url(full_url), code=302, **ctx.params)

        func = send_request_raw_supress if return_raw else send_request_supress
        resp = func(address, full_url, method=method,
                                    request=QRRequest(params=ctx.params, json_data=ctx.json_data, headers=ctx.headers, form=ctx.form))

        if resp.status_code not in [200]:
            raise ServiceUnavailableException(service)

        if return_raw:
            h = resp.headers if resp.__dict__.get('headers') else None
            return MethodResult(resp.content, raw_data=True, headers=h)

        # if resp.status_code != 200:
        #     raise ServiceUnavailableException(service)

        data = resp.get_json()

        if need_unpack:
            return MethodResult(unpack_dto_cls(**data))
        else:
            return MethodResult(unpack_dto_cls(data))

    if require_roles or use_guest_token:
        if require_roles:
            wrapper = require_role(require_roles)(wrapper)
        deco = with_jwt_token(extract_user=True, full_user=extract_full_user, auto_fill_guest=use_guest_token)
        wrapper = deco(wrapper)

    wrapper.__name__ = proxy_name
    return wrapper


# /api/v1/libraries
#@with_jwt_token(extract_username=False)
# @circuitBreaker.circuit([Service.LIBRARY], MethodResult('libraries not found', 503))
# def list_libraries_in_city(ctx: QRContext):
#     # full redirect
#     address = ctx.meta['services']['library']
#     resp = send_request_supress(address, 'api/v1/libraries',
#                                 request=QRRequest(params=ctx.params, json_data=ctx.json_data, headers=ctx.headers))
#
#     if resp.status_code != 200:
#         raise ServiceUnavailableException(Service.LIBRARY)
#
#     data = resp.get_json()
#     return MethodResult(PagingListLibraryDTO(**data))
#
#
# # /api/v1/libraries/<library_uid>/books
# #@with_jwt_token(extract_username=False)
# @circuitBreaker.circuit([Service.LIBRARY], MethodResult('books not found', 503))
# def list_books_in_library(ctx: QRContext, library_uid: int):
#     # full redirect
#     address = ctx.meta['services']['library']
#     resp = send_request_supress(address, f'api/v1/libraries/{library_uid}/books',
#                                 request=QRRequest(params=ctx.params, json_data=ctx.json_data, headers=ctx.headers))
#     if resp.status_code != 200:
#         raise ServiceUnavailableException(Service.LIBRARY)
#
#     data = resp.get_json()
#     return MethodResult(PagingListBookDTO(**data))
#
#
# # /api/v1/rating
# #@with_jwt_token(extract_username=False)
# @circuitBreaker.circuit([Service.RATING], MethodResult(ErrorDTO('Bonus Service unavailable'), 503))
# def get_user_rating(ctx: QRContext):
#     # full redirect
#     address = ctx.meta['services']['rating']
#     resp = send_request_supress(address, f'api/v1/rating',
#                                 request=QRRequest(params={}, json_data=ctx.json_data, headers=ctx.headers))
#     if resp.status_code != 200:
#         raise ServiceUnavailableException(Service.RATING)
#
#     data = resp.get_json()
#     return MethodResult(RatingDTO(**data))