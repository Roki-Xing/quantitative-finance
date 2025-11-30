import backtrader as bt

class HybridTrendATR(bt.Strategy):
    params = (
        ('risk', 0.02),
        ('short_window', 14),
        ('long_window', 50),
        ('atr_period', 14),
        ('stop_factor', 2),
    )

    def __init__(self):
        self.order = None
        self.entry_price = None

        self.sma_short = bt.indicators.SMA(self.data.close, period=self.params.short_window)
        self.sma_long = bt.indicators.SMA(self.data.close, period=self.params.long_window)
        self.atr = bt.indicators.ATR(self.data, period=self.params.atr_period)

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
            if (self.sma_short[0] > self.sma_long[0]) and (self.sma_short[-1] <= self.sma_long[-1]):
                atr_increase = self.atr[0] > self.atr[-1]
                if atr_increase:
                    risk_amt = self.broker.getvalue() * self.params.risk
                    atr_val = self.atr[0] if self.atr[0] > 0 else self.data.close[0] * 0.02
                    position_size = int(risk_amt / atr_val)
                    if position_size > 0:
                        self.order = self.buy(size=position_size)

        else:
            # Exit on MA crossunder
            if (self.sma_short[0] < self.sma_long[0]):
                self.order = self.close()
            # Stop-loss based on ATR
            elif self.entry_price and self.data.close[0] <= self.entry_price - self.atr[0] * self.params.stop_factor:
                self.order = self.close()
