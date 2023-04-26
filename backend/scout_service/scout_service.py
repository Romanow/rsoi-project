import sys
sys.path.append("..")
sys.path.append("../common")


from scout.ScoutRepository import *
from scout.dtos import *

from qr_server.Server import MethodResult, QRContext
from qr_server.Config import QRYamlConfig
from qr_server.TokenManager import require_token, JwtTokenManager
from qr_server.FlaskServer import FlaskServer

from common.common_api import health
from common.jwt_validator import JWTTokenValidator, require_role, with_jwt_token, TokenUser
from common.kafka_manager import KafkaConsumer


@with_jwt_token(extract_user=True, full_user=True)
@require_role(['user', 'admin'])
def register_event(ctx: QRContext, user: TokenUser):
    data = ctx.json_data
    time = data['time']
    event = data['event']
    data = data.get('data')
    if data is None:
        data = dict()

    ok = create_event(ctx.repository, event, time, user.login, data)
    if not ok:
        return MethodResult('failed to insert into db', 500)

    if not ok:
        return MethodResult('failed to insert into recent_viewed', 500)

    return MethodResult(DefaultResponseDTO())


@with_jwt_token(extract_user=True, full_user=True)
@require_role(['user', 'admin'])
def get_recent_viewed(ctx: QRContext, user: TokenUser):
    offset = ctx.params.get('offset')
    offset = int(offset) if offset else 0

    if offset > 0:  # for front-component logic
        return MethodResult([])

    data = ctx.repository.get_recent_viewed(user.login)
    if data is None:
        return MethodResult('failed to select from db', 500)

    return MethodResult(RecentViewedIDSDTO(data))


#@with_jwt_token(extract_user=True)
#@require_role(['admin'])
def get_events_in_interval(ctx: QRContext):
#def get_events_in_interval(ctx: QRContext, user: TokenUser):
    time_start = int(ctx.params.get('time_start'))
    time_end = int(ctx.params.get('time_end'))

    if time_start > time_end:
        return MethodResult('bad parameters: start cannot be bigger than end', 500)

    data = ctx.repository.get_in_interval(time_start, time_end)
    if data is None:
        return MethodResult('failed to select from db', 500)

    return MethodResult(EventsInIntervalDTO(data))

def update_recent_viewed(repository: IScoutRepository, user_login, time, event, data):
    entity_id, entity_type = None, None
    entities = ['book', 'series', 'author']
    for e in entities:
        if event == 'view_%s' % e:
            entity_type = e
            entity_id = data.get('%s_id'% e)

    if entity_type is None or entity_id is None:
        return True

    ok = repository.insert_recent_viewed(user_login, time, entity_id, entity_type)
    return ok


def create_event(repository: IScoutRepository, event, time, user_login, data):
    ok = repository.register_event(user_login, time, event, data)
    ok &= update_recent_viewed(repository, user_login, time, event, data)
    return ok

class ScoutServer(FlaskServer, ScoutRepository):
    """DI class🐕"""
    def __init__(self):
        FlaskServer.__init__(self)
        ScoutRepository.__init__(self)


def init_scout_server(server, token_man, config):
    server.init_server(config['app'])
    if config['app']['logging']:
        server.configure_logger(config['app']['logging'])
    server.register_manager(token_man)

    server.connect_repository(config['database'])
    server.set_recent_viewed_limit(config['app']['recent_viewed_limit'])

    server.register_method('/events', register_event, 'POST')
    server.register_method('/events', get_events_in_interval, 'GET')
    server.register_method('/users/recent_viewed', get_recent_viewed, 'GET')

    server.register_method('/manage/health', health, 'GET')


if __name__ == "__main__":
    config = QRYamlConfig()
    config.read_config('config.yaml')

    host = config['app']['host']
    port = config['app']['port']

    jwt = config['jwt']
    token_man = JWTTokenValidator(jwks_uri=jwt.jwks_uri, issuer=jwt.iss, audience=jwt.aud)

    server = ScoutServer()
    init_scout_server(server, token_man, config)

    def kafka_callback(msg):
        event = msg.topic()

        data = json.loads(msg.value())
        time, user_login = [data[k] for k in ['time', 'user_login']]
        [data.pop(k) for k in ['time', 'user_login']]

        create_event(server, event, time, user_login, data)

    kafka_consumer = KafkaConsumer(config=config.kafka_consumer.config.data,
                                   topics=config.kafka_consumer.topics.split(' '),
                                   logger=server.logger,
                                   callback=kafka_callback,
                                   create_missing_topics=True
                                   )
    kafka_consumer.logger = server.logger
    server.register_manager(kafka_consumer)

    server.run(host, port)
