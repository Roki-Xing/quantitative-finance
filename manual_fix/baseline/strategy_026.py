import backtrader as bt
import backtrader.indicators as btind

class MeanReversionBollingerBands(bt.Strategy):
    params = (
        ('maperiod', 20),  # period for Bollinger Bands
        ('devfactor', 2),  # standard deviations for Bollinger Bands
        ('stop_loss', 0.05),  # stop loss percentage
        ('take_profit', 0.10)  # take profit percentage
    )

    def __init__(self):
        self.order = None
        self.data_close = self.datas[0].close
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.bollinger = btind.BBands(period=self.p.maperiod, devfactor=self.p.devfactor, plot=False)

    def next(self):
        if self.data_close[0] > self.bollinger.lines.top[0] and self.position.size == 0:
            self.buy(size=self.broker.cash * 0.1)
        elif self.data_close[0] < self.bollinger.lines.bot[0] and self.position.size == 0:
            self.sell(size=self.broker.cash * 0.1)

        if self.position.size > 0:
            if self.data_close[0] > self.data_close[-1] * (1 + self.p.take_profit):
                self.sell(size=self.position.size)
                self.close()
            elif self.data_close[0] < self.data_close[-1] * (1 - self.p.stop_loss):
                self.close()
                self.sell(size=self.position.size)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed, order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Completed, Canceled, Margin, or Rejected')

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('Profit/loss %s' % trade.pnlcomm)