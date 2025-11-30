import backtrader as bt

class PriceVolumeStrategy(bt.Strategy):
    params = (
        ('fast_ma_len', 10),
        ('slow_ma_len', 30),
        ('stop_loss_pcnt', 0.05),
        ('take_profit_pcnt', 0.10),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(period=self.p.fast_ma_len)
        self.slow_ma = bt.indicators.SMA(period=self.p.slow_ma_len)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.fast_ma > self.slow_ma and self.data.close > self.data.close[-1]:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
        else:
            if self.position.size > 0:
                # Take profit
                if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit_pcnt):
                    self.order = self.close()
                    self.entry_price = None
                # Stop loss
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss_pcnt):
                    self.order = self.close()
                    self.entry_price = None
                # Exit on MA crossover
                elif self.fast_ma < self.slow_ma:
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
