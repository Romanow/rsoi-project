import faker
from russian_names import RussianNames
fake = faker.Faker()
name = RussianNames()

import qrook_db.DB as db
DB = db.DB('postgres', 'qrook_db_new', 'kurush', 'pondoxo', format_type='dict')
DB.create_data(__name__, in_module=True)


def create_users(n):
    data = []
    for i in range(n):
        d = dict()
        x = fake.profile()
        d['avatar'] = fake.image_url()
        d['email'] = x['mail']
        d['password'] = fake.password()
        d['login'] = x['username']

        x = name.get_person()
        d['name'], _, d['surname'] = x.split(' ')
        data.append(d)

    data = [[d['name'], d['surname'], d['email'], d['login'], d['password'], d['avatar']] for d in data]
    ok = DB.insert(DB.users, DB.users.name, DB.users.surname,
                   DB.users.email, DB.users.login, DB.users.password,
                   DB.users.avatar) \
        .values(data).exec()

    print(ok)
    if ok:
        DB.commit()


if __name__ == '__main__':
    create_users(100)