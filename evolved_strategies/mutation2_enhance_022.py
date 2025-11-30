import backtrader as bt
from backtrader.indicators import SMA, ATR

class AdvancedVolatilityBreakout(bt.Strategy):
    params = (
        ('fast_ma_period', 14),
        ('slow_ma_period', 28),
        ('atr_period', 10),
        ('atr_multiplier_entry', 1.5),
        ('atr_multiplier_tp', 2.0),
    )

    def __init__(self):
        self.fast_ma = SMA(self.data.close, period=self.params.fast_ma_period)
        self.slow_ma = SMA(self.data.close, period=self.params.slow_ma_period)
        self.atr = ATR(self.data, period=self.params.atr_period)
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
            # Entry condition: MA crossover + ATR increasing
            if (self.fast_ma > self.slow_ma and
                self.atr[-1] < self.atr[0] and
                self.atr[0] > self.params.atr_multiplier_entry * self.atr[-1]):
                self.order = self.buy()

        else:
            # Exit condition: MA crossunder or ATR drops
            if (self.fast_ma <= self.slow_ma or
                self.atr[0] < self.params.atr_multiplier_tp * self.atr[-1]):
                self.order = self.close()
