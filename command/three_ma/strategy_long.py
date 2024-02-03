from chan.chan_const import FractalType


class StrategyLong:
    def __init__(self, main):
        self.main = main

    def run_step(self):
        """
        逐根K线判断
        """
        if self.main.buy_direction == 'LONG':
            self.exec()

        self.make_plan()

    def exec(self):
        if self.main.buy_ts and self.main.is_plan_sell:
            self.main.sell(self.main.recent_data[0]['date'], self.main.recent_data[0]['open'])

        if (not self.main.buy_ts) and self.main.is_plan_buy:
            self.main.is_plan_buy = False
            if self.main.recent_data[0]['open'] >= self.main.buy_base_price:
                self.main.buy(self.main.recent_data[0]['date'], self.main.recent_data[0]['open'])
                self.main.sell_base_price = self.main.buy_base_price

        if self.main.buy_ts:
            if self.main.recent_data[0]['low'] < self.main.sell_base_price:
                self.main.sell(self.main.recent_data[0]['date'], self.main.sell_base_price)

    def make_plan(self):
        if self.main.recent_data[0]['cross_ma15_ma60']:
            self.main.lower_fractal = None

        if self.main.latest_fractal and self.main.latest_fractal.fractal_type == FractalType.BOTTOM:
            if not self.main.lower_fractal:
                self.main.lower_fractal = self.main.latest_fractal

            if self.main.lower_fractal.fractal_value > self.main.latest_fractal.fractal_value:
                self.main.lower_fractal = self.main.latest_fractal

            if not self.main.buy_ts and self.can_buy():
                self.main.is_plan_buy = True
                self.main.buy_direction = 'LONG'
                self.main.buy_base_price = self.main.lower_fractal.fractal_value

        if self.main.buy_ts and self.main.buy_direction == 'LONG':
            if self.can_sell():
                self.main.is_plan_sell = True

    def can_buy(self):
        conditions = [
            not self.main.recent_data[0]['cross_ma15_ma60'],
            self.main.recent_data[0]['ma432_angle'] > 0,
            self.main.recent_data[0]['ma60_angle'] > 0.06,
            self.main.recent_data[0]['ma15_angle'] > 0.1,
            self.main.recent_data[0]['ma60'] >= self.main.recent_data[0]['ma432'],
            self.main.recent_data[0]['ma15'] >= self.main.recent_data[0]['ma432'],
            # self.main.recent_data[0]['macd'] < 0,
        ]

        return all(conditions)

    def can_sell(self):
        conditions1 = [
            self.main.recent_data[0]['cross_ma15_ma60'],
            self.main.recent_data[0]['high'] < self.main.recent_data[0]['ma60'],
            # self.main.recent_data[0]['dif'] < 0,
            # self.main.recent_data[0]['dea'] < 0,
        ]

        conditions2 = [
            self.main.recent_data[0]['ma60'] < self.main.recent_data[0]['ma432'],
        ]

        return all(conditions1) or all(conditions2)
