import backtrader as bt
from backtrader.indicators import SMA, ATR

class EnhancedTrendFollowing(bt.Strategy):
    params = (
        ('fast_ma_period', 20),
        ('slow_ma_period', 50),
        ('risk_pct', 2.0),
        ('initial_stop_loss', 5.0),
        ('initial_take_profit', 10.0),
    )

    def __init__(self):
        self.fast_ma = SMA(period=self.params.fast_ma_period)
        self.slow_ma = SMA(period=self.params.slow_ma_period)
        self.atr = ATR(period=14)
        self.order = None
        self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        elif order.status in [order.Completed]:
            if order.isbuy():
                self.entry_price = order.executed.price
            elif order.issell():
                self.entry_price = None
            self.order = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.fast_ma > self.slow_ma:
                risk_amt = (self.params.risk_pct / 100) * self.broker.getvalue()
                atr_val = self.atr[0] if self.atr[0] > 0 else self.data.close[0] * 0.02
                size = int(risk_amt / atr_val)
                if size > 0:
                    self.order = self.buy(size=size)
        else:
            if self.fast_ma < self.slow_ma:
                self.order = self.close()
            elif self.entry_price and self.data.close[0] < (self.entry_price - self.atr[0] * 2):
                self.order = self.close()

    def stop(self):
        pass