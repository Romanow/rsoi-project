import os
from flask import Flask
from qrconfig import QRYamlConfig

from .models import db
from .oauth2 import config_oauth
from .routes import bp_oidc, bp_local, load_rsa_key_as_jwk

from common.jwt_validator import JWTTokenValidator

def create_app(name, config_file: str):
    config = QRYamlConfig()
    config.read_config(config_file)

    app = Flask(name, template_folder='./auth/templates')

    db = config.database
    db_uri = f'{db.connector}://{db.username}:{db.password}@{db.host}:{db.port}/{db.dbname}'

    app.config['jwt_config'] = config.jwt
    app.config['host'] = config.app.host
    app.config['port'] = config.app.port
    app.config['dummy_client_id'], app.config['dummy_client_secret'] = config.dummy_client.id, config.dummy_client.secret
    app.config.update(
        {
            'SECRET_KEY': 'some_super-secret_secret',   # smth for flask sessions

            'SQLALCHEMY_DATABASE_URI': db_uri,

            'OAUTH2_JWT_ENABLED': True,
            'OAUTH2_JWT_ISS': config.jwt.iss,
            'OAUTH2_JWT_KEY': load_rsa_key_as_jwk(app, private=True),  # config.jwt.key_path,
            'OAUTH2_JWT_ALG': config.jwt.alg,
            'OAUTH2_JWT_EXP': config.jwt.exp,
        }
    )

    app.jwt_token_validator = JWTTokenValidator(lambda: load_rsa_key_as_jwk(app, private=False), config.jwt['iss'], config.jwt['aud'])
    app.dummy_jwt_token_validator = JWTTokenValidator(lambda: load_rsa_key_as_jwk(app, private=False), config.dummy_client.iss, config.dummy_client.id)

    setup_app(app)
    return app


def setup_app(app):
    db.init_app(app)
    config_oauth(app)
    app.register_blueprint(bp_oidc, url_prefix='/oauth')
    app.register_blueprint(bp_local, url_prefix='')