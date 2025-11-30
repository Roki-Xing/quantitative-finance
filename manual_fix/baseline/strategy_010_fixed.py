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
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.fast_ma_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.slow_ma_period)
        self.atr = bt.indicators.AverageTrueRange(self.data, period=self.p.atr_period)
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Bullish breakout: price above both MAs and breaking out
            if (self.data_close[0] > self.slow_ma[0] and
                self.data_close[0] > self.fast_ma[0] and
                self.data_high[0] > self.data_close[-1] + self.atr[0] * self.p.atr_multiple):
                self.order = self.buy()
                self.entry_price = self.data_close[0]
            # Bearish breakout: price below both MAs and breaking down
            elif (self.data_close[0] < self.slow_ma[0] and
                  self.data_close[0] < self.fast_ma[0] and
                  self.data_low[0] < self.data_close[-1] - self.atr[0] * self.p.atr_multiple):
                self.order = self.sell()
                self.entry_price = self.data_close[0]
        else:
            # Long position exit
            if self.position.size > 0:
                if self.data_close[0] >= self.entry_price * (1 + self.p.take_profit_percent):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data_close[0] <= self.entry_price * (1 - self.p.stop_loss_percent):
                    self.order = self.close()
                    self.entry_price = None
            # Short position exit
            elif self.position.size < 0:
                if self.data_close[0] <= self.entry_price * (1 - self.p.take_profit_percent):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data_close[0] >= self.entry_price * (1 + self.p.stop_loss_percent):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
