from datetime import datetime, timedelta
from app import db
from app.exceptions import ValidationError

PRECISION = 6


class ExchangeRateHistory(db.Model):
    __tablename__ = 'exchange_rate_history'
    __table_args__ = (
        db.UniqueConstraint('date', 'from_', 'to',
                            name='_date_from_to_uc'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now)
    from_ = db.Column(db.String(100), nullable=False)
    to = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return "<ExchangeRateHistory> {}-{}".format(self.from_, self.to)

    def to_json(self):
        json_exchange_rate = {
            'id': self.id,
            'date': self.date,
            'from_': self.from_,
            'to': self.to,
            'rate': self.rate,
        }
        return json_exchange_rate

    @staticmethod
    def from_json(json_exchange_rate):
        required = ['date', 'from_', 'to', 'rate']

        valid_data = {}
        for field in required:
            data = json_exchange_rate.get(field)
            if data is None or data == '':
                raise ValidationError(
                    'exchange rate does not have a {}'.format(field))
            valid_data[field] = data

        try:
            date = datetime.strptime(valid_data['date'], '%Y-%m-%d')
        except Exception as e:
            raise ValueError('Valid date format YYYY-MM-DD')

        return ExchangeRateHistory(
            date=date,
            from_=valid_data['from_'],
            to=valid_data['to'],
            rate=valid_data['rate'],
        )

    def is_missing(self, date_selected):
        if len(self.past_7d(date_selected)) < 7:
            return True

        return False

    def past_7d_avg(self, date_selected=datetime.now()):
        """ Average of exchange rate for the past 7 days
        """
        rate_past_7d = [
            currency.rate for currency in self.past_7d(date_selected)]

        return round(sum(rate_past_7d) / len(rate_past_7d), PRECISION)

    def past_7d(self, date_selected=datetime.now()):
        date_past7d = date_selected - timedelta(days=7)

        start = date_past7d
        end = date_selected + timedelta(days=1)

        return ExchangeRateHistory.query.filter(
            db.and_(
                ExchangeRateHistory.date.between(start, end),
                ExchangeRateHistory.from_ == self.from_,
                ExchangeRateHistory.to == self.to,
            )
        ).all()

    def past_7d_variance(self, date_selected=datetime.now()):
        rate_past_7d = [
            currency.rate for currency in self.past_7d(date_selected)]

        max_rate, min_rate = max(rate_past_7d), min(rate_past_7d)

        return round(max_rate - min_rate, PRECISION)

    @staticmethod
    def add_or_get(json_data):
        obj = ExchangeRateHistory.from_json(json_data)

        exist = ExchangeRateHistory.query.filter(
            db.func.date(ExchangeRateHistory.date) == obj.date,
            ExchangeRateHistory.from_ == obj.from_,
            ExchangeRateHistory.to == obj.to,
        ).first()

        if not exist:
            db.session.add(obj)
            db.session.commit()
            db.session.refresh(obj)
            return obj

        return exist


class ExchangeRateList(db.Model):
    __tablename__ = 'exchange_rate_list'
    __table_args__ = (
        db.UniqueConstraint('from_', 'to',
                            name='_from_to_uc'),
    )

    id = db.Column(db.Integer, primary_key=True)
    from_ = db.Column(db.String(100), nullable=False)
    to = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return "<ExchangeRateList> {}-{}".format(self.from_, self.to)

    def __str__(self):
        return "{} - {}".format(self.from_, self.to)

    def to_json(self):
        json_exchange_rate = {
            'from_': self.from_,
            'to': self.to,
            'id': self.id
        }
        return json_exchange_rate

    @staticmethod
    def from_json(json_data):
        required = ['from_', 'to']

        valid_data = {}
        for field in required:
            data = json_data.get(field)
            if data is None or data == '':
                raise ValidationError(
                    'exchange rate does not have a {}'.format(field))
            valid_data[field] = data

        return ExchangeRateList(
            from_=valid_data['from_'],
            to=valid_data['to'],
        )

    @staticmethod
    def add_or_get(json_data):
        obj = ExchangeRateList.from_json(json_data)

        exist = ExchangeRateList.query.filter_by(
            from_=obj.from_,
            to=obj.to
        ).first()

        if not exist:
            db.session.add(obj)
            db.session.commit()
            return obj

        return exist
