import copy
import time
from datetime import datetime, timedelta

from flask import request, jsonify, Response

from qr_server.Server import MethodResult, QRContext
from qr_server.Config import QRYamlConfig
from qr_server.FlaskServer import FlaskServer
from qr_server.request_sending import *

from gateway.dtos import *
from gateway.utils import *
from gateway.proxy_api import *
from gateway.compound_api import *
from gateway.circuit_breaker import circuitBreaker

from common.job_queue import TASK_QUEUE, run_task_queue
from common.common_api import health
from common.jwt_validator import JWTTokenValidator


class GatewayServer(FlaskServer):
    def register_method(self, route: str, f, method_type: str):
        """register method"""
        func = lambda *args, **kwargs: self.__method(f, *args, **kwargs)
        func.__name__ = f.__name__
        self.methods[f.__name__] = \
            self.app.route(route, methods=[method_type])(func)

    def __method(self, f, *args, **kwargs):  # note: valuable changes; add to original FlaskServer
        ctx = super().create_context(request, self, meta=self.meta)
        ctx.set_managers(self.managers)
        in_msg = '[' + request.method + '] ' + request.url + '/' + request.query_string.decode()
        try:
            start = time.time()
            result = f(ctx, *args, **kwargs)
            end = time.time()
            msecs = int((end - start) * 1000)
            super().info('[' + str(msecs) + ' msecs]' + in_msg)

            if not isinstance(result, MethodResult) or result.__dict__.get('raw_data') is None:
                return result

            if result.raw_data:
                return result.result
            if result.status_code == 200:
                return jsonify(result.result)

            resp = Response(result.result, result.status_code)

            if result.headers is not None:
                for header, value in result.headers.items():
                    resp.headers[header] = value
            return resp

        except Exception as e:
            super().info(in_msg)
            super().exception(e)
            return self.default_err_msg, self.default_err_code

def init_gateway_server(server, meta, config, token_man):
    server.set_meta(meta)
    server.init_server(config['app'])
    server.connect_repository(config['database'])
    server.register_manager(token_man)

    if config['app']['logging']:
        server.configure_logger(config['app']['logging'])
        TASK_QUEUE.set_logger(server.logger)
        circuitBreaker.register_logger(server.logger)
        meta['logger'] = server.logger

    url_updater = lambda s: s[len('/api/v2/'):] if s.startswith('/api/v2/') else s

    # search
    server.register_method('/api/v2/library', method_type='GET', f=make_proxy('library', Service.SEARCH, SearchMainDTO, 'GET', url_updater, need_unpack=False, use_guest_token=True))
    server.register_method('/api/v2/books/<id>', method_type='GET', f=make_proxy('get_book', Service.SEARCH, BookFullDTO, 'GET', url_updater, use_guest_token=True))
    server.register_method('/api/v2/authors/<id>', method_type='GET', f=make_proxy('get_author', Service.SEARCH, AuthorFullDTO, 'GET', url_updater, use_guest_token=True))
    server.register_method('/api/v2/series/<id>', method_type='GET', f=make_proxy('get_series', Service.SEARCH, SeriesFullDTO, 'GET', url_updater, use_guest_token=True))

    # user_info
    server.register_method('/api/v2/users', method_type='GET', f=user_info)
    server.register_method('/', method_type='GET', f=home)

    # scout
    server.register_method('/api/v2/events', method_type='POST', f=make_proxy('register_event', Service.SCOUT, DefaultResponseDTO, 'POST', url_updater, need_unpack=False, require_roles=['user', 'admin']))

    #server.register_method('/api/v2/users/recent_viewed', method_type='GET', f=make_proxy('get_recent_viewed', Service.SCOUT, RecentViewedDTO, 'GET', url_updater, need_unpack=False, require_roles=['user', 'admin']))
    server.register_method('/api/v2/users/recent_viewed', method_type='GET', f=get_recent_viewed)
    server.register_method('/api/v2/report', method_type='GET', f=get_report_data)

    # file
    server.register_method('/api/v2/books/files/<path:req_path>', method_type='GET', f=make_proxy('get_book_file', Service.FILE, None, 'GET', url_updater, return_raw=True, require_roles=['user', 'admin']))

    redirect_auth = config.services.auth_service.redirect_auth
    if redirect_auth in [None, '', ' ']:
        redirect_auth = None
    server.register_method('/api/v2/oauth/authorize', method_type='GET', f=make_proxy('authorize_get', Service.AUTH, None, 'GET', url_updater, redirect=True, full_replace_url=redirect_auth))
    server.register_method('/api/v2/oauth/token', method_type='POST', f=make_proxy('get_token', Service.AUTH, None, 'POST', url_updater, return_raw=True))


if __name__ == "__main__":
    config = QRYamlConfig()
    config.read_config('config.yaml')

    host = config['app']['host']
    port = config['app']['port']

    services = config.services
    meta = {
        # todo add client_id here
        'services': {
            key: QRAddress(f'http://' + services[f'{name}_service']['host'], services[f'{name}_service']['port'])
            for key, name in zip(
                [Service.AUTH, Service.SEARCH, Service.SCOUT, Service.FILE],
                ['auth', 'search', 'scout', 'file']
            )
        },
    }

    circuitBreaker.register_config(config)
    circuitBreaker.register_meta(meta)

    jwt = config['jwt']
    token_man = JWTTokenValidator(jwks_uri=jwt.jwks_uri, issuer=jwt.iss, audience=jwt.aud,
                                  dummy_token=jwt.dummy_token)

    server = GatewayServer()
    init_gateway_server(server, meta, config, token_man)

    run_task_queue()

    server.run(host, port)
