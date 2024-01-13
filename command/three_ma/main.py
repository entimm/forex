import json
import os

import click
from chan.element.bar import Bar
from chan.element.kline import Kline
from chan.manager.bar_union_manager import BarUnionManager

from command.three_ma.strategy_long import StrategyLong
from command.three_ma.strategy_short import StrategyShort
from common.const import RESOURCES_PATH, PeriodEnum
from common.price_calculate import ma, ma_angle
from common.utils import get_forex_kline


@click.command()
@click.argument('period', type=str, default='D')
@click.argument('symbol', type=str)
def backtest_three_ma(period: str, symbol):
    strategy = Strategy()
    strategy.run(symbol, PeriodEnum[period])


class Strategy:
    def __init__(self):
        self.symbol = None
        self.period_enum = None

        self.bar_union_manager = BarUnionManager()

        self.is_plan_sell = False
        self.is_plan_buy = False

        self.buy_ts = None
        self.buy_direction = None
        self.buy_base_price = None
        self.sell_base_price = None
        self.sell_flag = 0

        self.order_list = []

        self.ma = [5, 15, 60, 432]

    def run(self, symbol, period_enum: PeriodEnum):
        """
        主控制
        """
        self.symbol = symbol
        self.period_enum = period_enum

        df = self.prepare_data_df()

        long_strategy = StrategyLong(self)
        short_strategy = StrategyShort(self)

        for index, row in df.iterrows():
            row = row.to_dict()
            fractal = self.bar_union_manager.add_bar(Bar(index, Kline(row)))
            long_strategy.run_step(row, fractal)
            short_strategy.run_step(row, fractal)

        # 结果输出
        result_json_file = os.path.join(RESOURCES_PATH, 'backtest', f'back_test_{self.symbol}.json')
        with open(result_json_file, 'w') as json_file:
            json.dump(self.order_list, json_file)

        print('打开浏览器查看回测结果 http://127.0.0.1:9999/backtest_result?symbol={}&period={}&ma={}'.
              format(self.symbol, self.period_enum.name, ','.join(map(str, self.ma))))

    def prepare_data_df(self):
        """
        准备数据
        """
        df = get_forex_kline(self.symbol, self.period_enum)

        for item in self.ma:
            df[f'ma{item}'] = ma(df, item)

        df['ma15_angle'] = ma_angle(df, 'ma15')
        df['ma60_angle'] = ma_angle(df, 'ma60')
        df['ma432_angle'] = ma_angle(df, 'ma432')
        df['cross_ma15_ma60'] = df['ma15'] > df['ma60']

        df = df.reset_index(names='date')
        df['time'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        return df

    def buy(self, ts, price):
        # 损大小判断
        if abs(1 - self.buy_base_price / price) * 100 > 0.8:
            return

        buy_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 2),
            'action': 'BUY',
            'direction': self.buy_direction,
            'out_price': round(self.buy_base_price, 2),
        }
        print(buy_info)
        self.order_list.append(buy_info)
        self.buy_ts = ts
        self.is_plan_buy = False

    def sell(self, ts, price):
        sell_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 2),
            'action': 'SELL',
            'direction': self.buy_direction,
            'flag': self.sell_flag,
        }
        print(sell_info)
        self.order_list.append(sell_info)
        self.buy_ts = None
        self.buy_direction = None
        self.is_plan_sell = False
        self.sell_flag = 0