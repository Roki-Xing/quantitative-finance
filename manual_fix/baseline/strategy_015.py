import backtrader as bt
from backtrader.indicators import RSI, MACD

class MomentumStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('stop_loss', 0.05),
        ('take_profit', 0.05),
    )

    def __init__(self):
        self.rsi = RSI(self.data, period=self.p.rsi_period)
        self.macd = MACD(self.data, fast=self.p.macd_fast, slow=self.p.macd_slow, signal=self.p.macd_signal)
        self.order = None

    def next(self):
        if self.order:
            return

        if self.rsi < 30 and self.macd.macd < 0 and self.macd.signal < 0:
            self.order = self.buy()
        elif self.rsi > 70 and self.macd.macd > 0 and self.macd.signal > 0:
            self.order = self.sell()

        if self.order:
            if self.position.size > 0 and self.data.close > self.data.close[0] + (self.data.close[0] * self.p.take_profit):
                self.order.close()
                self.order = None
            elif self.position.size < 0 and self.data.close < self.data.close[0] - (self.data.close[0] * self.p.stop_loss):
                self.order.close()
                self.order = None

cerebro = bt.Cerebro()
cerebro.addstrategy(MomentumStrategy)
cerebro.addindicator(bt.indicators.RSI, period=14)
cerebro.addindicator(bt.indicators.MACD, fast=12, slow=26, signal=9)
cerebro.adddata(bt.feeds.YahooFinanceCSVDataFeed, dataname='stock_data.csv')
cerebro.run()
cerebro.plot()