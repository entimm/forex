from chan.chan_const import FractalType


class StrategyLong:
    def __init__(self, main):
        self.main = main
        self.lower_fractal = None

    def run_step(self, row, fractal):
        """
        逐根K线判断
        """
        if self.main.buy_direction == 'LONG':
            self.exec(row)

        self.make_plan(row, fractal)

    def exec(self, row):
        if self.main.buy_ts and self.main.is_plan_sell:
            self.main.sell(row['date'], row['open'])

        if (not self.main.buy_ts) and self.main.is_plan_buy:
            if row['low'] >= self.main.buy_base_price:
                self.main.buy(row['date'], row['close'])
                self.main.sell_base_price = self.main.buy_base_price

        if self.main.buy_ts:
            if row['low'] < self.main.sell_base_price:
                self.main.sell(row['date'], min(self.main.sell_base_price, row['high']))

    def make_plan(self, row, fractal):
        if row['cross_ma15_ma60']:
            self.lower_fractal = None

        if fractal and fractal.fractal_type == FractalType.BOTTOM:
            if not self.lower_fractal:
                self.lower_fractal = fractal

            if self.lower_fractal.fractal_value > fractal.fractal_value:
                self.lower_fractal = fractal

            if not self.main.buy_ts and self.can_buy(row):
                self.main.is_plan_buy = True
                self.main.buy_direction = 'LONG'
                self.main.buy_base_price = self.lower_fractal.fractal_value

        if self.main.buy_ts and self.main.buy_direction == 'LONG':
            if self.can_sell(row):
                self.main.is_plan_sell = True
                self.main.sell_flag = 1
            elif self.can_sell2(row):
                self.main.is_plan_sell = True
                self.main.sell_flag = 2.1

    def can_buy(self, row):
        conditions = [
            not row['cross_ma15_ma60'],
            row['ma432_angle'] > 0,
            row['ma60_angle'] > 0.06,
            row['ma15_angle'] > 0.1,
            row['ma60'] >= row['ma432'],
            row['ma15'] >= row['ma432'],
        ]

        return all(conditions)

    def can_sell(self, row):
        conditions = [
            row['cross_ma15_ma60'],
            row['high'] < row['ma60'],
        ]

        return all(conditions)

    def can_sell2(self, row):
        conditions = [
            row['ma60'] < row['ma432'],
        ]

        return all(conditions)