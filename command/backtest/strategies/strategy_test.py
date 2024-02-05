class StrategyTest:
    def __init__(self, main):
        self.main = main

    def run_step(self):
        """
        逐根K线判断
        """
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
        if not self.main.buy_ts and self.can_buy():
            self.main.is_plan_buy = True
            self.main.buy_direction = 'LONG'
            self.main.buy_base_price = self.main.recent_data[0]['close'] * (1 - 0.008)

        if self.main.buy_ts and self.main.buy_direction == 'LONG':
            if self.can_sell():
                self.main.is_plan_sell = True

    def can_buy(self):
        conditions = [

        ]

        return all(conditions)

    def can_sell(self):
        conditions1 = [

        ]

        return all(conditions1)
