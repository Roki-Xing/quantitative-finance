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
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low

        self.bollinger = btind.BBands(self.data, period=self.p.maperiod, devfactor=self.p.devfactor)
        self.sma = btind.SMA(self.data, period=self.p.maperiod)

        self.order = None

    def next(self):
        if not self.position:
            if self.data_close[0] < (self.bollinger.lines.bot[0] + self.p.stop_loss * self.data_high[0]) and self.data_close[0] > self.bollinger.lines.bot[0]:
                self.order = self.buy(size=100)
                print('BUY CREATED')
            else:
            if self.data_close[0] > (self.sma[0] + self.p.take_profit * self.data_high[0]):
                self.close()
                self.order = self.sell(size=100)
                print('SELL CREATED')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.order = None