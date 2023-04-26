import functools

from authlib.integrations.flask_oauth2 import (
    AuthorizationServer, ResourceProtector)

from authlib.oauth2.rfc6749 import MissingAuthorizationError

from authlib.oauth2.rfc6750 import InsufficientScopeError



class AdvancedResourceProtector(ResourceProtector):
    def __call__(self, scope=None, operator='AND', optional=False):
        def wrapper(f):
            @functools.wraps(f)
            def decorated(*args, **kwargs):
                try:
                    self.acquire_token(scope, operator)
                except MissingAuthorizationError as error:
                    if optional:
                        return f(*args, **kwargs)
                    return 'no authorization', 401
                except InsufficientScopeError as error:     # note: added this exception catch, updated return messages
                    return 'insufficient scope', 401
                return f(*args, **kwargs)
            return decorated
        return wrapper