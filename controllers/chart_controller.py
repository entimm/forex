import json
from datetime import datetime

from chan import chan_config
from chan.chan import Chan
from flask import render_template, Blueprint, request, url_for, redirect
from numpy import bool_

from common.const import PeriodEnum
from common.config import config
from common.utils import row_to_kline, get_forex_kline

blueprint = Blueprint('chart', __name__)


def to_bool(value):
    if isinstance(value, bool_):
        return bool(value)
    return value


@blueprint.route('/chart')
def chart():
    symbol = request.args.get('symbol', '', type=str)
    period = request.args.get('period', '', type=str).upper()
    req_real = request.args.get('req_real', 0, type=int)
    chart_engine = request.args.get('chart_engine', 0, type=int)
    show_chan = request.args.get('show_chan', 0, type=int)
    socket_token = request.args.get('socket_token', '', type=str)

    limit = request.args.get('n', 0, type=int)

    price = request.args.get('price', 0, type=float)
    date = request.args.get('date', '', type=str)
    time = request.args.get('time', '', type=int)
    if time:
        date = datetime.fromtimestamp(abs(time)).strftime('%Y-%m-%d')

    if not symbol or not period:
        return redirect(url_for('chart.chart', symbol='XAUUSD', period=PeriodEnum.D.name, req_real=0))

    df = get_forex_kline(symbol, PeriodEnum[period])

    if show_chan and not limit:
        limit = 10000
    if limit:
        df = df.tail(limit)

    df['last_close'] = df['close'].shift(1)
    kline_list = df.apply(row_to_kline, axis=1).to_list()

    template_var = {
        'kline_list': kline_list,
        'period_list': {
            PeriodEnum.F1.name: '1分钟',
            PeriodEnum.F5.name: '5分钟',
            PeriodEnum.F15.name: '15分钟',
            PeriodEnum.F30.name: '30分钟',
            PeriodEnum.D.name: '天',
        },
        'request_args': {
            'symbol': symbol,
            'period': period,
            'req_real': req_real,
            'chart_engine': chart_engine,
            'show_chan': show_chan,
            'socket_token': socket_token,
            'date': date,
            'time': time,
            'n': limit,
            'price': price,
        },
        'indicator_config': config.get('indicator'),
    }

    if show_chan:
        chart_engine = 0

        tmp_chan_config_keys = ['force_stroke_vertex', 'force_segment_vertex', 'output_union', 'output_fractal',
                                'stroke_check_break', 'stroke_fix_sure']
        tmp_chan_config = {key: request.args.get(key, None, type=int) for key in tmp_chan_config_keys if
                           request.args.get(key, None, type=int) is not None}
        tmp_chan_config = config['chart']['chan'] | tmp_chan_config

        for key, value in tmp_chan_config.items():
            setattr(chan_config, key, value)

        chan_data = Chan(kline_list).output()
        chan_data['show_ma'] = request.args.get('show_ma', tmp_chan_config['show_ma'], type=int)
        chan_data['show_debug'] = request.args.get('show_debug', tmp_chan_config['show_debug'], type=int)

        template_var['chan_data'] = json.dumps(chan_data, default=lambda x: to_bool(x))
        template_var['request_args']['chart_engine'] = chart_engine

    return render_template('chart.html', **template_var)
