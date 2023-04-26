import os
import sys
from pathlib import Path

from flask import Flask, jsonify
from flask_cors import CORS
from flask import request, Response
import time
import gevent.pywsgi
from flask import Flask
from flask_cors import CORS

sys.path.append("..")
sys.path.append("../common")


from qr_server.FileManager import FlaskFileManager
from qr_server.Server import MethodResult, QRContext
from qr_server.Config import QRYamlConfig, IQRConfig
from qr_server.TokenManager import require_token, JwtTokenManager
from qr_server.FlaskServer import FlaskServer

from common.common_api import health
from common.jwt_validator import JWTTokenValidator, require_role, with_jwt_token, TokenUser
from common.kafka_manager import KafkaProducer


BOOKS_FOLDER = 'unknown'


@with_jwt_token(extract_user=True, full_user=True)
@require_role(['user', 'admin'])
def get_book(ctx: QRContext, req_path, user: TokenUser):
    man = ctx.managers['file_manager']
    dir = req_path[:req_path.rfind('/')]
    file = req_path[req_path.rfind('/')+1:]

    ctx.managers['kafka_producer'].produce_dict('download_book', {'file_path': req_path, 'user_login': user.login})
    return MethodResult(
        man.send_file(BOOKS_FOLDER + dir, file),
        raw_data=True)


# @require_token()
# def save_avatar(ctx: QRContext, user_id):
#     avatar = ctx.files['avatar']
#     filename = str(user_id) + '.jpg'
#     Path(AVATARS_FOLDER).mkdir(parents=True, exist_ok=True)
#     avatar.save(os.path.join(AVATARS_FOLDER, filename))
#
#     return MethodResult({'filename': filename}) # TODO WEB


class FileServer(FlaskServer):
    """DI class🐕"""

    def init_server(self, config: IQRConfig):
        app_name = config['app']['app_name']
        if app_name is None: app_name = 'app'

        debug = config['app']['debug']
        if debug is None: debug = False

        self.app = Flask(app_name)
        #self.app = Flask(app_name, static_folder=config['static_folder'], static_url_path='', )
        CORS(self.app)
        self.debug = debug

    def register_method(self, route: str, f, method_type: str, do_nothing: bool = False):
        """register method"""
        if do_nothing:
            func = lambda *args, **kwargs: self.__clear_method(f, *args, **kwargs)
            func.__name__ = f.__name__
            self.methods[f.__name__] = \
                self.app.route(route, methods=[method_type])(func)
        else:
            super().register_method(route, f, method_type)

    def __clear_method(self, f, *args, **kwargs):
        ctx = super().create_context(request, self, meta=self.meta)
        ctx.set_managers(self.managers)
        in_msg = '[' + request.method + '] ' + request.url + '/' + request.query_string.decode()
        try:
            start = time.time()
            result = f(ctx, *args, **kwargs)
            end = time.time()
            msecs = int((end - start) * 1000)
            super().info('[' + str(msecs) + ' msecs]' + in_msg)

            return result.result

        except Exception as e:
            super().info(in_msg)
            super().exception(e)
            return self.default_err_msg, self.default_err_code


def init_file_server(server, token_man, file_man, kafka_producer, config):
    server.init_server(config)
    if config['app']['logging']:
        server.configure_logger(config['app']['logging'])
        kafka_producer.logger = server.logger

    server.register_manager(token_man)
    server.register_manager(file_man)
    server.register_manager(kafka_producer)

    server.register_method('/books/files/<path:req_path>', get_book, 'GET', do_nothing=True)
    #server.register_method('/users/avatars', save_avatar, 'PATCH')

    server.register_method('/manage/health', health, 'GET')


if __name__ == "__main__":
    config = QRYamlConfig()
    config.read_config('config.yaml', )

    BOOKS_FOLDER = config.file_storage['books']

    host = config['app']['host']
    port = config['app']['port']

    jwt = config['jwt']
    token_man = JWTTokenValidator(jwks_uri=jwt.jwks_uri, issuer=jwt.iss, audience=jwt.aud)
    kafka_producer = KafkaProducer(config=config.kafka_producer.data)

    server = FileServer()
    file_man = FlaskFileManager()
    init_file_server(server, token_man, file_man, kafka_producer, config)
    server.run(host, port)
