import json
import os
import time
from collections import deque
from datetime import datetime

import click
import schedule
from chan.element.bar import Bar
from chan.element.kline import Kline
from chan.manager.bar_union_manager import BarUnionManager

from command.backtest.strategies.macd.long import StrategyLong
from command.backtest.strategies.macd.short import StrategyShort
from common.const import RESOURCES_PATH, PeriodEnum
from common.feishu import FeiShuRobot, MarkdownElement
from common.price_calculate import ma, ma_angle
from common.utils import get_forex_kline


@click.command()
@click.argument('period', type=str, default='D')
@click.argument('symbol', type=str)
def backtest2(period: str, symbol):
    main = Main(symbol, PeriodEnum[period])

    main.run()

    def job():
        print('开始执行...')
        main.run()

    schedule.every(1).minute.at(':00').do(job)
    while True:
        schedule.run_pending()
        print('等待执行...')
        time.sleep(1)


class Main:
    def __init__(self, symbol, period_enum: PeriodEnum):
        self.symbol = symbol
        self.period_enum = period_enum

        self.bar_union_manager = BarUnionManager()

        self.is_plan_sell = False
        self.is_plan_buy = False

        self.buy_ts = None
        self.buy_direction = None
        self.buy_base_price = None
        self.sell_base_price = None

        self.order_list = []

        self.ma = [5, 15, 60, 432]

        self.recent_data = deque(maxlen=10)

        self.lower_fractal = None
        self.higher_fractal = None
        self.latest_fractal = None

    def run(self):
        """
        主控制
        """
        print(datetime.now(), '回测中...')
        df = self.prepare_data_df()

        latest_row = df.iloc[-1]
        FeiShuRobot.instance('notify-heartbeat').send_info('最新行情', [
            MarkdownElement.make(f"**交易品种**: <font color='red'>{self.symbol} - {self.period_enum.name}</font>"),
            MarkdownElement.make(f"**行情时间**: <font color='red'>{latest_row['time']}</font>"),
            MarkdownElement.make(f"**开**: <font color='red'>{round(latest_row['open'], 5)}</font>"),
            MarkdownElement.make(f"**高**: <font color='red'>{round(latest_row['high'], 5)}</font>"),
            MarkdownElement.make(f"**低**: <font color='red'>{round(latest_row['low'], 5)}</font>"),
            MarkdownElement.make(f"**收**: <font color='red'>{round(latest_row['close'], 5)}</font>"),
        ])

        trategies = [
            StrategyLong(self),
            StrategyShort(self),
        ]

        for index, row in df.iterrows():
            row = row.to_dict()
            if len(self.recent_data) and self.recent_data[0]['time'] >= row['time']:
                continue

            self.recent_data.appendleft(row)

            fractal = self.bar_union_manager.add_bar(Bar(index, Kline(row)))
            self.latest_fractal = fractal
            for trategy in trategies:
                trategy.run_step()

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

        # 计算 MACD, 信号线 和 直方图
        df['ema12'] = df['close'].ewm(span=7).mean()
        df['ema26'] = df['close'].ewm(span=14).mean()
        df['dif'] = df['ema12'] - df['ema26']
        df['dea'] = df['dif'].ewm(span=6).mean()
        df['macd'] = df['dif'] - df['dea']

        df = df.reset_index(names='date')
        df['time'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        return df

    def buy(self, ts, price):
        # 损大小判断
        if abs(1 - self.buy_base_price / price) * 100 > 0.8:
            return
        if datetime.now().timestamp() - datetime.strptime(ts.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp() - 8 * 3600 <= 3600:
            FeiShuRobot.instance('notify-trade').send_ok('执行买入', [
                MarkdownElement.make(f"**交易品种**: <font color='red'>{self.symbol} - {self.period_enum.name}</font>"),
                MarkdownElement.make(f"**行情时间**: <font color='red'>{ts.strftime('%Y-%m-%d %H:%M:%S')}</font>"),
                MarkdownElement.make(f"**价格**: <font color='red'>{round(price, 5)}</font>"),
                MarkdownElement.make(f"**方向**: <font color='red'>{'做多' if self.buy_direction == 'LONG' else '做空'}</font>"),
                MarkdownElement.make(f"**止损**: <font color='red'>{round(self.buy_base_price, 5)}</font>"),
                MarkdownElement.make("[点击查看详情>>](http://127.0.0.1:9999/backtest_result?symbol={}&period={}&ma={})".format(self.symbol, self.period_enum.name, ','.join(map(str, self.ma)))),
            ])
        buy_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 5),
            'action': 'BUY',
            'direction': self.buy_direction,
            'out_price': round(self.buy_base_price, 5),
        }
        print(buy_info)
        self.order_list.append(buy_info)
        self.buy_ts = ts

    def sell(self, ts, price):
        if datetime.now().timestamp() - datetime.strptime(ts.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S').timestamp() - 8 * 3600 <= 3600:
            FeiShuRobot.instance('notify-trade').send_error('执行卖出', [
                MarkdownElement.make(f"**交易品种**: <font color='red'>{self.symbol} - {self.period_enum.name}</font>"),
                MarkdownElement.make(f"**行情时间**: <font color='red'>{ts.strftime('%Y-%m-%d %H:%M:%S')}</font>"),
                MarkdownElement.make(f"**价格**: <font color='red'>{round(price, 5)}</font>"),
                MarkdownElement.make(f"**方向**: <font color='red'>{'做多' if self.buy_direction == 'LONG' else '做空'}</font>"),
                MarkdownElement.make("[点击查看详情>>](http://127.0.0.1:9999/backtest_result?symbol={}&period={}&ma={})".format(self.symbol, self.period_enum.name, ','.join(map(str, self.ma)))),
            ])
        sell_info = {
            'date': ts.strftime('%Y-%m-%d %H:%M:%S'),
            'symbol': self.symbol,
            'price': round(price, 5),
            'action': 'SELL',
            'direction': self.buy_direction,
        }
        print(sell_info)
        self.order_list.append(sell_info)
        self.buy_ts = None
        self.buy_direction = None
        self.is_plan_sell = False

    def recent(self, i):
        return self.recent_data[i]
