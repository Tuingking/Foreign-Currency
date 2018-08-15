from datetime import datetime

from flask import jsonify, request, Response
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import ExchangeRateHistory, ExchangeRateList

from app.api import api
from app.api.errors import forbidden
from app.api.response import api_response, HttpResponse

"""
Usecase:
1. User wants to input daily exchange rate data
2. User has a list of exchange rates to be tracked
3. User wants to see the exchange rate trend from the most recent 7 data points
4. User wants to add an exchange rate to the list
5. User wants to remove an exchange rate from the list
"""


@api.route('/exchange_rates', methods=['POST'])
def input_daily_exchange_rate():
    """
    1. User wants to input daily exchange rate data

    Params:
    @date       %Y-%m-%d
    @from_      str
    @to         str
    @rate       float
    """

    try:
        exchange_rate_history = ExchangeRateHistory.add_or_get(request.json)
    except ValueError as e:
        return api_response(status=400, reason=str(e))

    res = {
        "history": exchange_rate_history.to_json()
    }

    return api_response(res, status=201)


@api.route('/exchange_rates/<string:date>', methods=['GET'])
def get_exchange_rate_by_date(date):
    """
    2. User has a list of exchange rates to be tracked

    Params:
    @date       %Y-%m-%d

    Return:
    List of rate on requested date + 7d average
    {
        "rates": [
            {
                "from_": "GBP",
                "to": "USD",
                "rate": 1.314233,
                "avg_last_7d": 1.316904
            },
        ]
    }

    7d average: avg_rage(from now to now-7)
    insufficient_date if daily data is missing
    """

    # Params in
    date_input = date
    if not date_input:
        date_input = datetime.now()
    else:
        date_input = datetime.strptime(date_input, '%Y-%m-%d')

    exchange_rate_history = ExchangeRateHistory.query.all()

    # Serialize
    results = []
    for exchange_rate in exchange_rate_history:
        past_7d = [e.to_json()['date']
                   for e in exchange_rate.past_7d(date_input)]

        if exchange_rate.is_missing(date_input):
            rate = "insuficcient data"
            avg_last_7d = ""
        else:
            rate = exchange_rate.rate
            avg_last_7d = exchange_rate.past_7d_avg(date_input)

        results.append({
            "from_": exchange_rate.from_,
            "to": exchange_rate.to,
            "rate": rate,
            "avg_last_7d": avg_last_7d,
            # "past_7d": past_7d
        })

    res = {
        "exchange_rates": results,
    }

    return api_response(res)


@api.route('/exchange_rates/trend', methods=['GET'])
def get_exchange_rate_trend():
    """
    3. User wants to see the exchange rate trend from the most recent 7 data points.

    Params:
    @from_      str
    @to         str

    Returns:
    {
        "average": 1.316904,
        "variance": MAX-MIN,
        "trend": [
            {
                "date": "2018-07-08",
                "rate": 1.417
            },
            ...
            {
                "date": "2018-07-02",
                "rate": 1.265
            }
        ]
    }

    """
    from_ = request.args.get('from')
    to = request.args.get('to')

    if from_ in [None, ''] or to in [None, '']:
        return HttpResponse.invalid_payload()

    history = ExchangeRateHistory.query.filter_by(from_=from_, to=to).first()
    if not history:
        return HttpResponse.not_found()

    exchange_rate_past_7d = history.past_7d()

    # Serializer
    trends = []
    for exchange_rate in exchange_rate_past_7d:
        trends.append({
            "date": exchange_rate.date,
            "rate": exchange_rate.rate
        })

    res = {
        "average": history.past_7d_avg(),
        "variance": history.past_7d_variance(),
        "trends": trends
    }

    return api_response(res)


@api.route('/exchange_rate_list', methods=['POST'])
def add_exchange_rate_to_list():
    """
    4. User wants to add an exchange rate to the list

    Params:
    @from_      str
    @to         str
    """
    json_exchange_rate_list = ExchangeRateList.add_or_get(request.json)

    res = {
        "list": json_exchange_rate_list.to_json()
    }

    return api_response(res, status=201)


@api.route('/exchange_rate_list', methods=['DELETE'])
def remove_exchange_rate_from_list():
    """
    5. User wants to remove an exchange rate from the list
    """
    # Params
    ids = request.json.get('ids', [])
    if not ids:
        return HttpResponse.invalid_payload()

    # Validate ids
    for id in ids:
        e = ExchangeRateList.query.filter_by(id=id).first()
        if not e:
            return HttpResponse.not_found()

    ExchangeRateList.query\
        .filter(
            ExchangeRateList.id.in_(ids))\
        .delete(synchronize_session=False)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return api_response(
        status=200,
        message="Data has been removed from list")
