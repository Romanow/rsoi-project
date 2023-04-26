from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2TokenMixin,
    OAuth2AuthorizationCodeMixin
)

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(128), unique=True)
    login = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128))
    surname = db.Column(db.String(128))
    avatar = db.Column(db.String(512))

    def __str__(self):
        return self.login

    def get_user_id(self):
        return self.id


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(
    #     db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    # user = db.relationship('User')


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')
