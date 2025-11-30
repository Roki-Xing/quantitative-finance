import backtrader as bt
import backtrader.indicators as btind

class VolatilityBreakoutStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 10),
        ('slow_ma_period', 20),
        ('atr_period', 20),
        ('atr_multiple', 2.0),
        ('stop_loss_percent', 0.05),
        ('take_profit_percent', 0.05),
    )

    def __init__(self):
        self.fast_ma = bt.indicators.SimpleMovingAverage(period=self.p.fast_ma_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(period=self.p.slow_ma_period)
        self.atr = bt.indicators.AverageTrueRange(period=self.p.atr_period)
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low

    def next(self):
        if not self.position:
            if self.data_close > self.slow_ma > self.fast_ma and self.data_high > self.data_close + (self.p.atr * self.p.atr_multiple):
                self.buy(size=100)
                self.broker.set_stop_loss(self.data_close * (1 - self.p.stop_loss_percent))
                self.broker.set_take_profit(self.data_close * (1 + self.p.take_profit_percent))
            else:
            if self.data_close < self.slow_ma or self.data_low < self.data_close - (self.p.atr * self.p.atr_multiple):
                self.sell(size=100)
                self.broker.set_stop_loss(self.data_close * (1 - self.p.stop_loss_percent))
                self.broker.set_take_profit(self.data_close * (1 + self.p.take_profit_percent))