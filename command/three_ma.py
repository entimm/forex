import json
import os

import click
from chan.chan_const import FractalType
from chan.element.bar import Bar
from chan.element.kline import Kline
from chan.manager.bar_union_manager import BarUnionManager

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

        self.lower_fractal = None

        self.order_list = []

        self.ma = [5, 15, 60, 432]

    def run(self, symbol, period_enum: PeriodEnum):
        """
        主控制
        """
        self.symbol = symbol
        self.period_enum = period_enum

        df = self.prepare_data_df()

        for index, row in df.iterrows():
            row = row.to_dict()
            self.run_step(index, row)

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

    def run_step(self, index, row):
        """
        逐根K线判断
        """
        # 执行卖出计划
        if self.buy_ts and self.is_plan_sell:
            self.sell(row['date'], row['open'])

        if (not self.buy_ts) and self.is_plan_buy:
            # 当天最低价高于基准价就执行买入计划
            if row['low'] >= self.buy_base_price:
                self.buy(row['date'], row['close'])
                self.sell_base_price = self.buy_base_price

        if self.buy_ts:
            # 盘中跌破基准价就卖出
            if row['low'] < self.sell_base_price:
                self.sell(row['date'], min(self.sell_base_price, row['high']))

        # 做计划
        fractal = self.bar_union_manager.add_bar(Bar(index, Kline(row)))
        self.make_plan(row, fractal)

    def make_plan(self, row, fractal):
        # 金叉后底分型重置
        if row['cross_ma15_ma60']:
            self.lower_fractal = None

        if fractal and fractal.fractal_type == FractalType.BOTTOM:
            if not self.lower_fractal:
                self.lower_fractal = fractal

            if self.lower_fractal.fractal_value > fractal.fractal_value:
                self.lower_fractal = fractal

            # 死叉卖，维护基准价格
            if not self.buy_ts and self.can_buy(row):
                self.is_plan_buy = True
                self.buy_base_price = self.lower_fractal.fractal_value

        if self.buy_ts:
            # 金叉后遇到顶分型
            if self.can_sell(row):
                self.is_plan_sell = True
                self.sell_flag = 1
            # 60均线跌破432均线
            elif self.can_sell2(row):
                self.is_plan_sell = True
                self.sell_flag = 2.1

    @staticmethod
    def can_buy(row):
        conditions = [
            not row['cross_ma15_ma60'],
            row['ma432_angle'] > 0,
            row['ma60_angle'] > 0.06,
            row['ma15_angle'] > 0.1,
            row['ma60'] >= row['ma432'],
            row['ma15'] >= row['ma432'],
        ]

        return all(conditions)

    @staticmethod
    def can_sell(row):
        conditions = [
            row['cross_ma15_ma60'],
            row['high'] < row['ma60'],
        ]
        return all(conditions)

    @staticmethod
    def can_sell2(row):
        conditions = [
            row['ma60'] < row['ma432'],
        ]
        return all(conditions)

    def buy(self, ts, price):
        # 损大小判断
        if (1 - self.buy_base_price / price) * 100 > 0.8:
            return

        buy_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 2),
            'action': 'BUY',
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
            'flag': self.sell_flag,
        }
        print(sell_info)
        self.order_list.append(sell_info)
        self.buy_ts = None
        self.is_plan_sell = False
        self.sell_flag = 0
