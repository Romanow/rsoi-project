from behave import *
from common import *

use_step_matcher("parse")


@step("cite client exists")
def step_create_event_initiator(context):
    try:
        auth_url = context.auth_service_url
        search_url = context.search_service_url
        scout_url = context.scout_service_url
    except:
        print('Some service urls are not defined! can\'t create event initiator')
        raise
    context.event_init = EventInitiator(auth_url, search_url, scout_url)


@given('"{service}" runs on "{url}"')
def step_service_url(context, service, url):
    context.__dict__[service+'_url'] = url
    pass
