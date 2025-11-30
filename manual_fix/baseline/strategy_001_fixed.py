import backtrader as bt

class TrendFollowingStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 20),
        ('slow_ma_period', 50),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.fast_ma_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.slow_ma_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
            elif self.crossover < 0:
                self.order = self.sell()
                self.entry_price = self.data.close[0]
        else:
            # Long position exit
            if self.position.size > 0:
                if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
            # Short position exit
            elif self.position.size < 0:
                if self.data.close[0] <= self.entry_price * (1 - self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] >= self.entry_price * (1 + self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
