import backtrader as bt
from backtrader.indicators import SMA, ATR, RSI

class AdaptiveMultiFactorStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 10),
        ('medium_ma_period', 20),
        ('slow_ma_period', 50),
        ('rsi_period', 14),
        ('atr_period', 14),
        ('atr_multiple', 3.0),
        ('risk_factor', 0.01),
    )

    def __init__(self):
        self.fast_ma = SMA(self.data.close, period=self.params.fast_ma_period)
        self.medium_ma = SMA(self.data.close, period=self.params.medium_ma_period)
        self.slow_ma = SMA(self.data.close, period=self.params.slow_ma_period)
        self.rsi = RSI(self.data.close, period=self.params.rsi_period)
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

        atr_val = self.atr[0] if self.atr[0] > 0 else self.data.close[0] * 0.02

        if not self.position:
            # Triple MA alignment + RSI filter
            trend_strength = (self.fast_ma > self.medium_ma) and (self.medium_ma > self.slow_ma)
            volatility_filter = self.rsi < 30 or self.rsi > 70

            if trend_strength and volatility_filter:
                risk_per_trade = self.broker.getvalue() * self.params.risk_factor
                position_size = int(risk_per_trade / (atr_val * self.params.atr_multiple))

                if position_size > 0:
                    self.order = self.buy(size=position_size)

        else:
            # Trailing stop based on ATR
            if self.entry_price:
                trailing_stop = self.entry_price - atr_val * self.params.atr_multiple

                if self.data.close[0] < trailing_stop:
                    self.order = self.close()
                # Exit on MA crossunder
                elif self.fast_ma < self.medium_ma:
                    self.order = self.close()
