from flask import Blueprint

api = Blueprint('api', __name__)

from . import currency_exchange


@api.route('', methods=['GET'])
def index():
    return "Hello world"
