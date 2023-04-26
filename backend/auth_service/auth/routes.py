import functools
import time
from pathlib import Path

import requests
from authlib.jose import JsonWebKey, jwt, jwk
from authlib.jose.rfc7518._backends._key_cryptography import RSAKey
from flask import Blueprint, request, session
from flask import render_template, redirect, jsonify
from requests.auth import HTTPBasicAuth
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from .models import db, User, OAuth2Client, OAuth2Token
from .oauth2 import authorization, require_oauth, generate_user_info
import flask

from common.jwt_validator import with_jwt_token_raw, TokenUser, require_role


bp_oidc = Blueprint('oidc_routes', 'oidc')
bp_local = Blueprint('local_routes', 'local')

def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None

def load_user_from_session(f):
    def wrapper(*args, **kwargs):
        user = current_user()
        kwargs['user'] = user
        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper

def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


# ==== OIDC block ====
def load_rsa_key_as_jwk(app=None, private: bool = False):
    #public_key_path = Path("auth/etc") / "jwtRS256.key.pub"  # todo hardcoooode! from request
    if app is None:
        app = flask.current_app

    c = app.config['jwt_config']

    key_file = c['private_key'] if private else c['public_key']

    public_key = jwk.dumps(Path(key_file).read_bytes(), kty='RSA')
    #public_key = RSAKey.import_key(public_key_path.read_bytes())
    public_key["use"] = "sig"
    public_key["alg"] = "RS256"
    public_key["kid"] = c['kid']
    return {'keys': [public_key]}


@bp_oidc.route("/.well-known/jwks")
def jwks_endpoint():
    return jsonify(load_rsa_key_as_jwk())


@bp_oidc.route('/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    if user is None:
        session['redirect_after_login'] = request.url
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return jsonify(dict(error.get_body()))
        return render_template('authorize.html', user=user, grant=grant)

    grant_user = user if (user and request.form.get('confirm')) else None
    return authorization.create_authorization_response(grant_user=grant_user)


@bp_oidc.route('/token', methods=['POST'])
def create_token():
    resp = authorization.create_token_response()
    return resp


@bp_oidc.route('/userinfo')
@require_oauth('profile')
def get_userinfo():
    return jsonify(generate_user_info(current_token.user, current_token.scope))


# ==== local block ====
@bp_local.route('/', methods=['GET'])
def home():
    user = current_user()
    if user:
        tokens = OAuth2Token.query.filter_by(user_id=user.id).all()
        ids = list(set([t.client_id for t in tokens]))
        clients = OAuth2Client.query.filter(OAuth2Client.client_id.in_(ids)).all()
    else:
        clients = []
    return render_template('home.html', user=user, clients=clients, is_admin=(user.role == 'admin') if user else False)


@bp_local.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = User.query.filter_by(login=login).first()
        if not user or user.password != password:
            return 'incorrect login or password', 401

        session['id'] = user.id

        redirect_to = '/'
        if session.get('redirect_after_login'):
            redirect_to = session['redirect_after_login']
            session.pop('redirect_after_login')
        return redirect(redirect_to)

    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []
    return render_template('login.html', user=user, clients=clients)


@bp_local.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/login')


@bp_local.route('/create_client', methods=('GET', 'POST'))
#@with_jwt_token_raw(extract_user=True)
@load_user_from_session
@require_role(['admin'], raw=True)
def create_client(user: TokenUser):
    if request.method == 'GET':
        return render_template('create_client.html')

    form = request.form
    client_id = gen_salt(24)
    client = OAuth2Client(client_id=client_id)
    # Mixin doesn't set the issue_at date
    client.client_id_issued_at = int(time.time())
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)

    client_metadata = {
        "client_name": form["client_name"],
        "client_uri": form["client_uri"],
        "grant_types": split_by_crlf(form["grant_type"]),
        "redirect_uris": split_by_crlf(form["redirect_uri"]),
        "response_types": split_by_crlf(form["response_type"]),
        "scope": form["scope"],
        "token_endpoint_auth_method": form["token_endpoint_auth_method"]
    }
    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()
    return redirect('/')


@bp_local.route('/create_user', methods=('GET', 'POST'))
#@with_jwt_token_raw(extract_user=True)
@load_user_from_session
@require_role(['admin'], raw=True)
def create_user(user: TokenUser):
    if request.method == 'GET':
        return render_template('create_user.html')

    form = request.form
    user_data = {
        'role': 'user',
        "email": form["email"],
        "login": form["login"],
        "password": form["password"],
        "name": form["name"],
        "surname": form["surname"],
    }
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()
    return redirect('/')

