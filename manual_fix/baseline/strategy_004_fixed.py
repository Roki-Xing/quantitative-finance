import backtrader as bt
import backtrader.indicators as btind

class VolatilityBreakoutStrategy(bt.Strategy):
    params = (
        ('atr_period', 14),
        ('atr_multiple', 2.0),
        ('stop_loss_pcnt', 0.05),
        ('take_profit_pcnt', 0.05),
    )

    def __init__(self):
        self.atr = btind.ATR(self.data, period=self.p.atr_period)
        self.highest = btind.Highest(self.data.high, period=20)
        self.lowest = btind.Lowest(self.data.low, period=20)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy on breakout above recent high with volatility confirmation
            if self.data.high[0] > self.highest[-1]:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
            # Sell on breakdown below recent low
            elif self.data.low[0] < self.lowest[-1]:
                self.order = self.sell()
                self.entry_price = self.data.close[0]
        else:
            if self.position.size > 0:
                if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit_pcnt):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss_pcnt):
                    self.order = self.close()
                    self.entry_price = None
            elif self.position.size < 0:
                if self.data.close[0] <= self.entry_price * (1 - self.p.take_profit_pcnt):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] >= self.entry_price * (1 + self.p.stop_loss_pcnt):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
