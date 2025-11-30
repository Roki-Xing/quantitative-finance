import backtrader as bt
import backtrader.indicators as btind

class MultiFactorStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 20),
        ('slow_ma_period', 50),
        ('rsi_period', 14),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.fast_ma = btind.SMA(self.data.close, period=self.p.fast_ma_period)
        self.slow_ma = btind.SMA(self.data.close, period=self.p.slow_ma_period)
        self.rsi = btind.RSI(self.data.close, period=self.p.rsi_period)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy: MA cross up + RSI oversold
            if self.fast_ma > self.slow_ma and self.rsi < 30:
                self.order = self.buy()
                self.entry_price = self.data.close[0]
            # Sell: MA cross down + RSI overbought
            elif self.fast_ma < self.slow_ma and self.rsi > 70:
                self.order = self.sell()
                self.entry_price = self.data.close[0]
        else:
            if self.position.size > 0:
                if self.data.close[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data.close[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
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
