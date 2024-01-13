import json
import os

from flask import Blueprint, render_template, request

from common.const import RESOURCES_PATH, PeriodEnum
from common.utils import row_to_kline, get_forex_kline

blueprint = Blueprint('backtest', __name__)


@blueprint.route('/backtest_result_data')
def backtest_result_data():
    symbol = request.args.get('symbol', 'XAUUSD', type=str)
    result_json_file = os.path.join(RESOURCES_PATH, 'backtest',
                                    f'back_test_{symbol}.json' if symbol else 'back_test.json')
    with open(result_json_file, 'r') as file:
        trades = json.load(file)

    result_list = generate_order_leverage(trades)

    return result_list


@blueprint.route('/backtest_result')
def backtest_result():
    symbol = request.args.get('symbol', 'XAUUSD', type=str)
    period = request.args.get('period', 'D', type=str)
    ma = request.args.get('ma', '5,15,60,432', type=str).split(',')
    result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{symbol}.json' if symbol else 'back_test.json')
    kline_list = []
    if symbol:
        df = get_forex_kline(symbol, PeriodEnum[period])
        kline_list = df.apply(row_to_kline, axis=1).to_list()
    if not os.path.exists(result_json_file):
        return '没有数据'
    with open(result_json_file, 'r') as file:
        trades = json.load(file)

    get_color_func = get_color()

    template_var = {
        'kline_list': kline_list,
        'backtest_trades': trades,
        'indicator_config': {
            'ma': [{'period': item, 'color': get_color_func(), 'size': 1} for item in ma]
        },
        'request_args': request.args.to_dict(),
    }

    return render_template('backtest_result.html', **template_var)


def generate_order_leverage(trades, initial_capital=100000):
    leverage = 150
    bet_percentage = 0.1

    order = {}
    capital = initial_capital
    buy_date = ''
    buy_direction = ''
    buy_price = 0
    hold_vol = 0

    for trade in trades:
        if trade["action"] == "BUY":
            buy_date = trade["date"]
            buy_price = trade["price"]
            buy_direction = trade["direction"]

            hold_vol = (capital * bet_percentage * leverage // trade["price"])
        elif trade["action"] == "SELL":
            profit = round((trade["price"] - buy_price) * hold_vol, 2)
            profit = profit * (1 if buy_direction == 'LONG' else -1)
            capital = capital + profit

            hold_vol = 0

            order[trade["date"]] = {
                'capital': round(capital, 2),
                'symbol': trade.get('symbol', ''),
                'name': '',
                'profit': profit,
                'price': round(trade["price"], 2),
                'date_desc': f'{buy_date} - {trade["date"]}'
            }
            print(order[trade["date"]])

    return order


def get_color():
    i = 0
    color = [
        '#930606',
        '#ECAB07',
        '#EF15DE',
        '#16DE45',
        '#6E28E5',
        '#E50B33',
        '#16B9DE',
    ]

    def _get_color():
        nonlocal i, color
        i += 1
        return color[i % len(color)]

    return _get_color
