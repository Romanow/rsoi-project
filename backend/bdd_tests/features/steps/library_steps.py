from behave import *
use_step_matcher("parse")

def go_to_page(context, page, id=None):
    if page == 'home':
        context.data = context.event_init.home_page()
    elif page == 'account':
        context.info_data, context.data = context.event_init.user_page()
    elif page == 'author':
        context.info_data, context.data = context.event_init.author_page(id)
    elif page == 'series':
        context.info_data, context.data = context.event_init.series_page(id)
    elif page == 'book':
        context.info_data = context.event_init.book_page(id)

def find_by_entity_id(items, entity, id):
    for x in items:
        if (x['type'], x['id']) == (entity, id):
            return True
    return False

def find_by_entity_at_least(items, entity, count):
    cnt = 0
    for x in items:
        if x['type'] == entity:
            cnt += 1
    print(cnt, count, items, entity)
    return cnt >= count

def check_info_data(data, entity, id):
    return data['type'] == entity and data['id'] == id


@when('user goes to "{page}" page')
def step_impl(context, page):
    go_to_page(context, page)

@given('user is at "{page}" page')
def step_impl(context, page):
    go_to_page(context, page)

@when('user goes to "{page}" page with id = "{id}"')
def step_impl(context, page, id):
    go_to_page(context, page, id)

@given('user is at "{page}" page with id = "{id}"')
def step_impl(context, page, id):
    go_to_page(context, page, id)

@step('user visited "{page}" page with id = "{id}"')
def step_impl(context, page, id):
    go_to_page(context, page, id)


@then('user gets "{count}" cards of "{entity_list}"')
def step_impl(context, count, entity_list):
    if count == 'multiple':
        count = 2
    elif count == 'one':
        count = 1
    entity_list = entity_list.replace(',', '').replace(' and ', ' ').split(' ')
    for entity in entity_list:
        if not find_by_entity_at_least(context.data, entity, count):
            raise NotImplementedError(f'entity {entity} is not observed in enough quantity ({count}) on current page')

@step('user observes "{entity}" card with id = "{id}"')
def step_impl(context, entity, id):
    print(entity, id, context.data)
    if not find_by_entity_id(context.data, entity, int(id)):
        raise Exception(f'entity {entity} with id {id} is not observed on current page')


@then('user gets information about "{entity}" with id = "{id}"')
def step_impl(context, entity, id):
    id = int(id)
    if not check_info_data(context.info_data, entity, id):
        raise NotImplementedError(f'expected to get info about entity {entity} with id {id}')


@step('user gets card of "{entity}" with id = "{id}"')
def step_impl(context, entity, id):
    if not find_by_entity_id(context.data, entity, int(id)):
        raise Exception(f'entity {entity} with id {id} is not found on requested page')
