import backtrader as bt
import backtrader.indicators as btind

class VolatilityBreakoutStrategy(bt.Strategy):
    params = (
        ('fast_ma_period', 14),
        ('slow_ma_period', 28),
        ('atr_period', 14),
        ('stop_loss', 0.05),
        ('take_profit', 0.05)
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.fast_ma = btind.SMA(period=self.params.fast_ma_period)
        self.slow_ma = btind.SMA(period=self.params.slow_ma_period)
        self.atr = btind.ATR(period=self.params.atr_period)
        self.order = None

    def next(self):
        if self.order:
            return

        if self.data_close[0] > self.slow_ma[0] and self.data_close[-1] < self.slow_ma[-1]:
            self.buy()
            self.order = self.buy()
            self.stop_loss = self.data_close[0] - (self.atr[0] * self.params.stop_loss)
            self.broker.set_stoploss(self.stop_loss)

        elif self.data_close[0] < self.slow_ma[0] and self.data_close[-1] > self.slow_ma[-1]:
            self.sell()
            self.order = self.sell()
            self.stop_loss = self.data_close[0] + (self.atr[0] * self.params.stop_loss)
            self.broker.set_stoploss(self.stop_loss)

        if self.position:
            if self.data_close[0] > self.params.take_profit * self.data_high[0]:
                self.close()
                self.order = None
            elif self.data_close[0] < self.params.take_profit * self.data_low[0]:
                self.close()
                self.order = None