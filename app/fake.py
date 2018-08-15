import random
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import ExchangeRateHistory, ExchangeRateList

preset = (
    ('GBP', 'USD', 7),
    ('USD', 'GBP', 7),
    ('USD', 'IDR', 7),
    ('JYP', 'IDR', 4),
)


def exchange_rate_history():
    now = datetime.now()

    fake = Faker()
    i = 0
    for currency in preset:
        curr = now
        past_nd = now - timedelta(days=currency[2])

        while curr > past_nd:
            exist = ExchangeRateHistory.query.filter(
                db.func.date(ExchangeRateHistory.date) == curr.date(),
                ExchangeRateHistory.from_ == currency[0],
                ExchangeRateHistory.to == currency[1],
            ).first()

            if exist:
                curr -= timedelta(days=1)
                continue

            e = ExchangeRateHistory(
                date=curr,
                from_=currency[0],
                to=currency[1],
                rate=round(random.uniform(1.0, 10.0), 2))
            db.session.add(e)
            try:
                db.session.commit()
                curr -= timedelta(days=1)
            except IntegrityError:
                db.session.rollback()


def exchange_rate_list():
    fake = Faker()
    for currency in preset:
        e = ExchangeRateList(
            from_=currency[0],
            to=currency[1])
        db.session.add(e)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
