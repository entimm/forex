import math
import os
from urllib.parse import urlencode

import pandas as pd

from common.const import RESOURCES_PATH, MQL_PATH


def get_forex_kline(symbol, period_enum):
    csv_file = os.path.join(MQL_PATH, 'Files', f'{symbol}_{period_enum.name}.csv')
    if not os.path.exists(csv_file):
        csv_file = os.path.join(RESOURCES_PATH, f'{symbol}_{period_enum.name}.csv')

    df = pd.read_csv(csv_file, parse_dates=['date'], index_col='date')

    return df


def create_link(request_args, update_args, highlight_condition, text):
    request_args = request_args | update_args
    highlight_attr = 'class ="highlight"' if highlight_condition else ''

    return f'<a href="{create_href(request_args)}" {highlight_attr}>{text}</a>'


def create_href(params):
    params = {key: int(value) if isinstance(value, bool) else value for key, value in params.items()}

    return f'?{urlencode(params)}'


def row_to_kline(row):
    return {
        'time': row.name.strftime("%Y-%m-%d %H:%M:%S"),
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close'],
        'volume': row['volume'],
        'last_close': row['last_close'] if not math.isnan(row.get('last_close', math.nan)) else '',
    }
