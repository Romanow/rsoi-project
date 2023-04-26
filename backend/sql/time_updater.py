from qrookDB import DB
from random import randrange
from datetime import timedelta
from datetime import datetime

def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)

db = DB.DB('postgres', 'qrook_db_new', 'kurush', 'pondoxo', 'localhost', '5432')
db.create_data(__name__, in_module=True)
db.create_logger(app_name='qrookdb_test')

data = db.select(db.series).all()
for x in data:
    id = x['id']
    d1 = datetime.strptime('5/5/2021 1:30 PM', '%m/%d/%Y %I:%M %p')
    d2 = datetime.strptime('5/9/2021 4:50 AM', '%m/%d/%Y %I:%M %p')
    d = random_date(d1, d2)
    ok = db.update(db.series, auto_commit=True).set(updated_at=d).where(id=id).exec()