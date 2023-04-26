from qrookDB.data import QRTable
from datetime import datetime
import json
from abc import abstractmethod

import qr_server.Repository as rep
from Library import LibraryRepository
users = QRTable()

class IScoutRepository(LibraryRepository):
    @abstractmethod
    def register_event(self, user_login, time, event: str, data: dict):
        """register event"""

class ScoutRepository(IScoutRepository, rep.QRRepository):
    def __init__(self):
        super().__init__()
        self.limit = 10
        # todo 10 to config

    def set_recent_viewed_limit(self, n):
        self.limit = n

    def register_event(self, user_login, time, event: str, data: dict):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        data = data.copy()
        data['user_login'] = user_login
        str_data = json.dumps(data)
        time = datetime.fromtimestamp(time)

        i = self.db.intelligence
        ok = self.db.insert(i, i.time, i.event, i.data, auto_commit=True) \
            .values([time, event, str_data]).exec()
        return ok

    def insert_recent_viewed(self, user_login, time, entity_id, entity_type):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        time = datetime.fromtimestamp(time)

        rv = self.db.recent_viewed
        op = self.db.operators
        data = self.db.select(rv).where(user_login=user_login).order_by(rv.time, desc=True).all()

        if len(data) > self.limit:
            bad_ids = [x['id'] for x in data[self.limit-1:]]
            self.db.delete(rv, auto_commit=True).where(user_login=user_login, id=op.In(*bad_ids)).exec()

        for d in data:
            if d['entity_id'] == entity_id and d['entity_type'] == entity_type:
                return True

        ok = self.db.insert(rv, rv.user_login, rv.time, rv.entity_id, rv.entity_type, auto_commit=True) \
            .values([user_login, time, entity_id, entity_type]).exec()
        return ok

    def get_recent_viewed(self, user_login):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        rv = self.db.recent_viewed

        data = self.db.select(rv).where(user_login=user_login).order_by(rv.time, desc=True).all()

        data = [{'id':x['entity_id'], 'entity_type': x['entity_type']} for x in data]
        return data

        # author_ids = [x['entity_id'] for x in data if x['entity_type'] == 'author']
        # book_ids = [x['entity_id'] for x in data if x['entity_type'] == 'book']
        # series_ids = [x['entity_id'] for x in data if x['entity_type'] == 'series']
        # return {'author_ids': author_ids, 'book_ids': book_ids, 'series_ids': series_ids}

    def get_in_interval(self, time_start, time_end):
        if self.db is None:
            raise Exception('DBAdapter not connected to database')

        convert = lambda ts: datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        time_start = convert(time_start)
        time_end = convert(time_end)

        i = self.db.intelligence
        op = self.db.operators
        data = self.db.select(i, i.event, i.data).where(time=op.Between(time_start, time_end)).all()
        return data


