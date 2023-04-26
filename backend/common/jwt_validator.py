# module originates here: https://github.com/marpaia/jwks

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.parse import urljoin

import flask
from flask import request
from jose import jwt
from pydantic import BaseModel
import requests

from typing import Any, Callable, Optional

from qr_server import MethodResult, QRContext, IQRManager

from .errors import *

DEFAULT_ALGORITHMS = ["RS256"]

@dataclass
class TokenUser:
    role: str
    email: str = None
    login: str = None
    name: str = None
    surname: str = None
    avatar: str = None

class JSONWebKey(BaseModel):
    alg: str
    kty: str
    use: str
    n: str
    e: str
    kid: str

    # x5t: str
    # x5c: List[str]

    def rsa_key(self) -> Dict[str, str]:
        return {
            "kty": self.kty,
            "kid": self.kid,
            "use": self.use,
            "n": self.n,
            "e": self.e,
        }


class JSONWebKeySet(BaseModel):
    keys: List[JSONWebKey]


class JWTTokenValidator(IQRManager):
    jwks_uri: str  #
    audience: str
    issuer: str  # url of identity provider
    algorithms: List[str]

    public_keys: Dict[str, JSONWebKey]
    public_keys_last_refreshed: float = 0.
    key_refresh_interval: int

    @staticmethod
    def get_name() -> str:
        return "jwt_token_validator"

    def __init__(
            self,
            jwks_uri: str,
            issuer: str,
            audience: str = None,
            algorithms=None,
            key_refresh_interval=3600,
            dummy_token=None
    ):

        if algorithms is None:
            algorithms = DEFAULT_ALGORITHMS

        self.jwks_uri = jwks_uri
        self.audience = audience
        self.issuer = issuer
        self.algorithms = algorithms
        self.public_keys = {}
        self.key_refresh_interval = key_refresh_interval
        self.default_key_refresh_interval = key_refresh_interval
        self.dummy_token = dummy_token
        self.refresh_keys()

    def keys_need_refresh(self) -> bool:

        need = (time.time() - self.public_keys_last_refreshed) > self.key_refresh_interval
        if need:
            self.key_refresh_interval = self.default_key_refresh_interval
        return need

    def refresh_keys(self) -> None:
        if callable(self.jwks_uri):
            jwks = self.jwks_uri()
            jwks = JSONWebKeySet.parse_obj(jwks)
        else:
            try:
                resp = requests.get(self.jwks_uri)
                jwks = JSONWebKeySet.parse_raw(resp.text)
            except Exception as e:
                print(f'Warning: failed to load jwks for jwt validator! will automatically retry at next request...')
                self.key_refresh_interval = -1
                return
        self.public_keys_last_refreshed = time.time()
        self.public_keys.clear()
        for key in jwks.keys:
            self.public_keys[key.kid] = key

    def validate_token(self, token: str, *, num_retries: int = 0) -> Dict[str, Any]:
        # Before we do anything, the validation keys may need to be refreshed.
        # If so, refresh them.
        if self.keys_need_refresh():
            self.refresh_keys()

        # Try to extract the claims from the token so that we can use the key ID
        # to determine which key we should use to validate the token.
        try:
            unverified_claims = jwt.get_unverified_header(token)
        except Exception:
            raise InvalidTokenError("Unable to parse key ID from token")

        # See if we have the key identified by this key ID.
        try:
            key = self.public_keys[unverified_claims["kid"]]
        except KeyError:
            # If we don't have this key and this is the first attempt (ie: we
            # haven't refreshed keys yet), then try to refresh the keys and try
            # again.
            if num_retries == 0:
                self.refresh_keys()
                return self.validate_token(token, num_retries=1)
            else:
                raise KeyIDNotFoundError

        # Now that we have found the key identified by the supplied token's key
        # ID, we try to use it to decode and validate the supplied token.
        try:
            payload = jwt.decode(
                token,
                key.rsa_key(),
                algorithms=self.algorithms,
                audience=self.audience,
                issuer=self.issuer,
                options={'verify_at_hash': False}   # если да (в токене есть at_hash), то он хочет еще access_token для проверки
            )

        # A series of errors may be thrown if the token is invalid. Here, we
        # catch several of them and attempt to return a relatively specific
        # exception. All of these exceptions subclass AuthError so that the
        # caller can just catch AuthError if they want.
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token is expired")
        except jwt.JWTClaimsError:
            raise InvalidClaimsError("Check the audience and issuer")
        except Exception:
            raise InvalidHeaderError("Unable to parse authentication token")

        return payload


def with_jwt_token(extract_user=False, full_user=False, auto_fill_guest: bool = False):
    def wrapper(f):
        def decorator(ctx: QRContext, *args, **kwargs):
            name = JWTTokenValidator.get_name()
            token_validator = ctx.get_manager(name)
            if token_validator is None:
                return MethodResult(f'context does not contain jwt validator: expected "{name}" manager', 401)

            auth = ctx.headers.get('Authorization')
            if auth is None and auto_fill_guest and token_validator.dummy_token:
                token = token_validator.dummy_token
                ctx.headers['Authorization'] = 'Bearer ' + token
            else:
                if auth is None:
                    return MethodResult('no auth data found', 401)
                if not auth.startswith('Bearer '):
                    return MethodResult('Bearer token expected', 401)
                token = auth[len('Bearer '):]
            try:
                payload = token_validator.validate_token(token)     # todo duplicate below
                if extract_user:
                    kwargs['user'] = TokenUser(role=payload['sub'])
                    if full_user:
                        kwargs['user'].email = payload['email']
                        kwargs['user'].login = payload['nickname']
                        kwargs['user'].name = payload['name']
                        kwargs['user'].surname = payload['family_name']
                        kwargs['user'].avatar = payload['avatar']
                return f(ctx, *args, **kwargs)
            except JWT_ERRORS as e:
                return MethodResult(f'invalid token: {str(e)}', 401)
            except Exception as e:
                return MethodResult(str(e), 500)
        decorator.__name__ = f.__name__
        return decorator
    return wrapper

def with_jwt_token_raw(extract_user=False, full_user=False, dummy=False):
    def wrapper(f):
        def decorator(*args, **kwargs):
            app = flask.current_app

            if dummy:
                token_validator = app.dummy_jwt_token_validator
            else:
                token_validator = app.jwt_token_validator
            if token_validator is None:
                return MethodResult(f'app does not contain jwt validator', 401)

            auth = request.headers.get('Authorization')
            if auth is None:
                return 'no auth data found', 401
            if not auth.startswith('Bearer '):
                return 'Bearer token expected', 401
            token = auth[len('Bearer '):]
            try:
                payload = token_validator.validate_token(token)
                if extract_user:
                    kwargs['user'] = TokenUser(role=payload['sub'])
                    if full_user:
                        kwargs['user'].email = payload['email']
                        kwargs['user'].login = payload['nickname']
                        kwargs['user'].name = payload['name']
                        kwargs['user'].surname = payload['family_name']
                        kwargs['user'].avatar = payload['avatar']

                return f(*args, **kwargs)
            except JWT_ERRORS as e:
                return f'invalid token: {e}', 401
            except Exception as e:
                return str(e), 500
        decorator.__name__ = f.__name__
        return decorator
    return wrapper


def require_role(roles=None, raw=False):
    def wrapper(f):
        def decorator(*args, **kwargs):
            if roles:
                if kwargs.get('user') is None:
                    resp = 'no user specified', 401
                    return resp if raw else MethodResult(*resp)
                user = kwargs['user']
                role = user.role
                if role not in roles:
                    resp = f'not authorized for role {role}', 403
                    return resp if raw else MethodResult(*resp)
                return f(*args, **kwargs)
        decorator.__name__ = f.__name__
        return decorator
    return wrapper
