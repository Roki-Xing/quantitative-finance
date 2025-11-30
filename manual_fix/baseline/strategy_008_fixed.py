import backtrader as bt
import backtrader.indicators as btind

class MeanReversionBollingerStrategy(bt.Strategy):
    params = (
        ('maperiod', 20),
        ('devfactor', 2),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.data_close = self.datas[0].close
        self.bollinger = btind.BBands(self.data.close, period=self.p.maperiod, devfactor=self.p.devfactor)
        self.sma = btind.SMA(self.data.close, period=self.p.maperiod)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy when price near lower band
            if self.data_close[0] < self.bollinger.lines.bot[0]:
                self.order = self.buy()
                self.entry_price = self.data_close[0]
            # Sell when price near upper band
            elif self.data_close[0] > self.bollinger.lines.top[0]:
                self.order = self.sell()
                self.entry_price = self.data_close[0]
        else:
            if self.position.size > 0:
                if self.data_close[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data_close[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
            elif self.position.size < 0:
                if self.data_close[0] <= self.entry_price * (1 - self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.data_close[0] >= self.entry_price * (1 + self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
