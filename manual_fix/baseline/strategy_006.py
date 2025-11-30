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
        self.fast_ma = btind.SMA(period=self.p.fast_ma_period)
        self.slow_ma = btind.SMA(period=self.p.slow_ma_period)
        self.rsi = btind.RSI(period=self.p.rsi_period)
        self.order = None

    def next(self):
        if not self.position:
            if self.fast_ma > self.slow_ma and self.rsi < 30:
                self.buy(size=self.broker.getvalue() * 0.05)
                self.order = self.buy()
            elif self.fast_ma < self.slow_ma and self.rsi > 70:
            self.sell(size=self.position.size)
            self.order = self.sell()
            else:
            if self.position.size > 0 and self.rsi > 70:
                self.sell(size=self.position.size)
                self.order = self.sell()
            elif self.position.size < 0 and self.rsi < 30:
                self.buy(size=abs(self.position.size))
                self.order = self.buy()

        if self.position:
            if self.position.size > 0 and self.fast_ma < self.slow_ma:
                if self.position.price * (1 - self.p.stop_loss) < self.data.close:
                    self.sell(size=self.position.size)
                    self.order = self.sell()
                elif self.position.size < 0 and self.fast_ma > self.slow_ma:
                if self.position.price * (1 + self.p.stop_loss) > self.data.close:
                    self.buy(size=abs(self.position.size))
                    self.order = self.buy()

            if self.position.size > 0 and self.fast_ma > self.slow_ma:
                if self.data.close > self.position.price * (1 + self.p.take_profit):
                    self.sell(size=self.position.size)
                    self.order = self.sell()
                elif self.position.size < 0 and self.fast_ma < self.slow_ma:
                if self.data.close < self.position.price * (1 - self.p.take_profit):
                    self.buy(size=abs(self.position.size))
                    self.order = self.buy()