import backtrader as bt

class TrendFollowingStrategy(bt.Strategy):
    params = (
        ('short_window', 20),
        ('long_window', 50),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.short_ma = bt.indicators.SMA(period=self.p.short_window)
        self.long_ma = bt.indicators.SMA(period=self.p.long_window)
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0 and self.data.close[0] > self.data.close[-1] * (1 - self.p.stop_loss):
                self.order = self.buy()
                self.entry_price = self.data.close[0]
        else:
            if self.position.size > 0:
                # Exit on bearish crossover
                if self.crossover < 0:
                    self.order = self.close()
                    self.entry_price = None
                # Take profit
                elif self.data.close[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                # Stop loss
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
