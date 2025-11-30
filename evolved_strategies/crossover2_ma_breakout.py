import backtrader as bt

class TrendBreakoutFusion(bt.Strategy):
    params = (
        ('fast_period', 9),
        ('slow_period', 21),
        ('stop_loss_factor', 0.05),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.MovingAverageSimple(self.data.close, period=self.params.fast_period)
        self.slow_ma = bt.indicators.MovingAverageSimple(self.data.close, period=self.params.slow_period)

        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

        self.order = None
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status == order.Completed:
            if order.isbuy():
                self.entry_price = order.executed.price
            elif order.issell():
                self.entry_price = None
            self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Entry on MA crossover
            if self.crossover > 0:  # Fast crosses above slow
                self.order = self.buy()
        else:
            # Exit on MA crossunder
            if self.crossover < 0:  # Fast crosses below slow
                self.order = self.close()
            # Stop-loss
            elif self.entry_price and self.data.close[0] < self.entry_price * (1 - self.params.stop_loss_factor):
                self.order = self.close()
