import json

from behave import *

use_step_matcher("parse")

def login_check(context, login, password):
    token = context.event_init.login(login, password)
    context.login_status = token is not None
    if token is None:
        return False
    context.creds = (login, password)
    return True


@given("user is logged in with credentials")
def step_impl(context):
    creds = json.loads(context.text)
    login, password = creds['username'], creds['password']
    if not login_check(context, login, password):
        raise Exception('failed to login')

@then('user gets user info')
def step_impl(context):
    if context.info_data['name'] != context.creds[0]:
        raise NotImplementedError(f'expected to get info about user')


@when("user enters {username}  and {password} in request form")
def step_impl(context, username, password):
    login_check(context, username, password)


@then("user's login status is {status}")
def step_impl(context, status):
    if str(context.login_status) != status:
        raise Exception(f'expected login status to be {status}, got {context.login_status}')