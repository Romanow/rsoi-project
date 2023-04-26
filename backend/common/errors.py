class AuthError(Exception):
    pass


class KeyIDNotFoundError(AuthError):
    pass


class InvalidTokenError(AuthError):
    pass


class InvalidHeaderError(InvalidTokenError):
    pass


class InvalidClaimsError(InvalidTokenError):
    pass


class TokenExpiredError(AuthError):
    pass

# note: important to be tuple, not list! (if using as "except JWT_ERRORS as e: ...)
JWT_ERRORS = (AuthError, KeyIDNotFoundError, InvalidTokenError, InvalidHeaderError, InvalidClaimsError, TokenExpiredError)