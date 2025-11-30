import backtrader as bt
import backtrader.indicators as btind

class MomentumStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('rsi_threshold', 30),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.macd = btind.MACD(self.data.close, period_me1=self.p.macd_fast,
                               period_me2=self.p.macd_slow, period_signal=self.p.macd_signal)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.rsi < self.p.rsi_threshold and self.macd.macd > self.macd.signal:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
        else:
            if self.position.size > 0:
                if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
                elif self.rsi > 70:
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
