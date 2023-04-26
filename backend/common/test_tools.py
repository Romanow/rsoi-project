import json
import os
import sys
from contextlib import contextmanager

import psycopg2
from qr_server.Server import QRContext
from qr_server.Config import IQRConfig, QRYamlConfig
from qrookDB.DB import DB


class ContextCreator:
    def __init__(self):
        self.data = None
        self.managers = []
        self.repo = None

    def context(self, json_data=None, params=None, headers=None, form=None, files=None):
        json_data = dict() if json_data is None else json_data
        params = dict() if params is None else params
        headers = dict() if headers is None else headers
        form = dict() if form is None else form
        files = dict() if files is None else files
        self.data = [json_data, params, headers, form, files]
        return self

    def with_token_manager(self, token_manager, auth_id=None):
        self.managers.append(token_manager)
        if auth_id is not None:
            token = token_manager.make_token(user_id=auth_id)
            self.data[2]['Authorization'] = token
        return self

    def with_manager(self, manager):
        self.managers.append(manager)
        return self

    def with_repository(self, repository):
        self.repo = repository
        return self

    def build(self):
        ctx = QRContext(*self.data, repository=self.repo)
        for m in self.managers:
            ctx.add_manager(m.get_name(), m)
        return ctx


class DBTestManager:
    def __init__(self, config: IQRConfig, db_init_filename, db_procedures_filename=None):
        self.config = config
        self.conn = [config['connector'],
                config['dbname'],
                config['username'],
                config['password'],
                config['host'],
                config['port']
                ]
        self.init_file = db_init_filename
        self.init_proc_file = db_procedures_filename
        self.test_db_name = config['dbname'] + '_test'

    def init_test_db(self):
        db = DB(*self.conn, format_type='dict')
        db.enable_database_drop()
        try:
            db.exec(f"DROP DATABASE {self.test_db_name}").exec()
            ok = db.exec(f"CREATE DATABASE {self.test_db_name}").exec()
            if not ok:
                raise Exception('failed to recreate database')

            print("DB recreated:", self.test_db_name, ok)
        except Exception as e:
            pass

        with open(self.init_file) as f:
            query = f.read()

        old_name = self.conn[1]
        self.conn[1] = self.test_db_name
        db = DB(*self.conn, format_type='dict')
        self.conn[1] = old_name

        db.create_logger(level='ERROR')
        ok = db.exec(query).exec()
        db.commit()
        if ok:
            ok = self.__init_procedures(self.test_db_name)
        if not ok:
            raise Exception('failed to create tables')
        return self.test_db_name

    def __init_procedures(self, new_dbname):
        if not self.init_proc_file:
            return True
        with open(self.init_proc_file) as f:
            query = f.read()

        conn = psycopg2.connect(dbname=new_dbname, user=self.config['username'],
                                password=self.config['password'], host=self.config['host'], port=self.config['port'])
        cur = conn.cursor()
        try:
            cur.execute(query)
            conn.commit()
        except psycopg2.errors.DuplicateObject:
            pass
        cur.close()
        conn.close()
        return True

    def exit_test_db(self):
        db = DB(*self.conn, format_type='dict')
        db.enable_database_drop()
        try:
            ok = db.exec(f"DROP DATABASE {self.test_db_name}").exec()
            if not ok:
                raise Exception('failed to drop database')
            print("DB dropped:", self.test_db_name, ok)
        except Exception as e:
            pass

    def fill_data(self, table, filename):
        with open(filename) as f:
            data = json.load(f)

        columns = [table.__dict__[k] for k in data[0].keys()]
        data = [x.values() for x in data]
        ok = table.insert(*columns, auto_commit=True).values(data).exec()
        if not ok:
            raise Exception('cannot fill the data')

    def fill_data_from_dir(self, db, dirname):
        files = list(os.listdir(dirname))
        files.sort(key=lambda x: len(x) + 10*x.count('_'))
        for filename in files:
            with open(os.path.join(dirname, filename)) as f:
                data = json.load(f)
            tablename = os.path.basename(filename)
            tablename = tablename[:tablename.rfind('.')]
            table = db.__dict__[tablename]

            columns = [table.__dict__[k] for k in data[0].keys()]
            data = [x.values() for x in data]
            ok = table.insert(*columns, auto_commit=True).values(data).exec()
            if not ok:
                raise Exception('cannot fill the data')


def setUpDBTester(cls, test_path, with_proc=False):
    config = QRYamlConfig()
    config.read_config(test_path+'config.test.yaml')
    return setUpDBTesterFromConfig(config, cls, test_path, with_proc)

def setUpDBTesterFromConfig(config, cls, test_path, with_proc=False):
    proc_path = None if not with_proc else test_path+'test_db_scheme_procedures.sql'
    cls.dbtest_man = DBTestManager(config['database'], test_path+'test_db_scheme.sql', proc_path)
    test_db_name = cls.dbtest_man.init_test_db()
    config['database']['dbname'] = test_db_name
    return config


@contextmanager
def assert_not_raises(self, exc_type):
    try:
        yield None
    except exc_type:
        tb = sys.exc_info()[2]
        msg = '{} raised'.format(exc_type.__name__)
        raise self.failureException(msg).with_traceback(tb) from None
