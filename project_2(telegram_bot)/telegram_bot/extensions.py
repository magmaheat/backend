import json
import requests
from config import *


class APIException(Exception):
    pass


class Examination:
    @staticmethod
    def exam(message):
        full = message.split(' ')
        if len(full) != 3:
            raise APIException('Неверно введены параметры!')
        quote, base, amount = full

        if quote not in keys.keys():
            raise APIException(f'Валюты - {quote} нет в списке доступных'
                               f', либо она введена неверно!')

        if base not in keys.keys():
            raise APIException(f'Валюты - {base} нет в списке доступных!')

        if quote == base:
            raise APIException("Нельзя сравнивать одинаковые валюты")

        if not amount.isdigit():
            raise APIException(f'{amount} не является числом!')

        return quote, base, amount


class Api:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={keys[quote]}&tsyms={keys[base]}')
        total_base = json.loads(r.content)[keys[base]] * float(amount)
        text = f'Цена валюты {quote} в количестве {amount} в валюте {base} - {total_base}'
        return text



