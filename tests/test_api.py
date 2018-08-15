import unittest
import json
import re
from base64 import b64encode
from datetime import datetime, timedelta
from app import create_app, db, fake
from app.models import ExchangeRateHistory, ExchangeRateList


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_input_daily_exchange(self):
        response = self.client.post(
            '/api/exchange_rates',
            headers=self.get_api_headers(),
            data=json.dumps({
                "date": "2018-01-01",
                "from_": "USD",
                "to": "IDR",
                "rate": 1.5
            }))
        self.assertEqual(response.status_code, 201)

    def test_input_daily_exchange_invalid_date_format(self):
        response = self.client.post(
            '/api/exchange_rates',
            headers=self.get_api_headers(),
            data=json.dumps({
                "date": "01-01-2018",
                "from_": "USD",
                "to": "IDR",
                "rate": 1.5
            }))
        self.assertEqual(response.status_code, 400)

    def test_add_to_list(self):
        response = self.client.post(
            '/api/exchange_rate_list',
            headers=self.get_api_headers(),
            data=json.dumps({
                "from_": "USD",
                "to": "IDR",
            }))

        exchange_rate_list = ExchangeRateList.query.filter_by(
            from_="USD",
            to="IDR"
        ).first()

        self.assertIsNotNone(exchange_rate_list)

    def test_remove_from_list(self):
        add_to_list = (
            ('GBP', 'EUR'),
            ('CHF', 'USD'),
        )

        just_inserted_ids = []
        for currency in add_to_list:
            response = self.client.post(
                '/api/exchange_rate_list',
                headers=self.get_api_headers(),
                data=json.dumps({
                    "from_": currency[0],
                    "to": currency[1],
                }))

            json_response = json.loads(response.get_data(as_text=True))
            just_inserted_ids.append(json_response['data']['list']['id'])

        count = ExchangeRateList.query.count()
        self.assertEqual(count, 2)

        response = self.client.delete(
            '/api/exchange_rate_list',
            headers=self.get_api_headers(),
            data=json.dumps({
                "ids": just_inserted_ids
            })
        )

        self.assertEqual(response.status_code, 200)

    def test_past_7d(self):
        fake.exchange_rate_history()

        preset = fake.preset
        first_preset = preset[0]
        from_, to = first_preset[0], first_preset[1]

        exchange_rate = ExchangeRateHistory.query.filter_by(
            from_=from_,
            to=to
        ).first()

        self.assertEqual(len(exchange_rate.past_7d()), 7)
