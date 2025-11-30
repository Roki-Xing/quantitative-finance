import backtrader as bt
import backtrader.indicators as btind

class MomentumStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('rsi_threshold', 30),
        ('macd_threshold', 0),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.macd = btind.MACD(self.data.close, fast=self.p.macd_fast, slow=self.p.macd_slow)
        self.signal = btind.MACD(self.macd, plot=False).diff()

    def next(self):
        if self.position.size == 0:
            if self.rsi < self.p.rsi_threshold and self.signal > 0:
                self.buy()
            elif self.position.size > 0:
            if self.rsi > 50 and self.signal < 0:
                self.close()
                self.sell()
            elif self.rsi > 70:
                self.close()
                self.sell()

        if self.position.size > 0:
            stop_loss_price = self.data.close[0] * (1 - self.p.stop_loss)
            take_profit_price = self.data.close[0] * (1 + self.p.take_profit)
            if self.data.close[0] <= stop_loss_price:
                self.close()
                self.sell()
            elif self.data.close[0] >= take_profit_price:
                self.close()
                self.buy()