import backtrader as bt
import backtrader.indicators as btind

class MultiFactorComprehensiveStrategy(bt.Strategy):
    params = (
        ('maperiod1', 20),
        ('maperiod2', 50),
        ('maperiod3', 100),
        ('stop_loss', 0.05),
        ('take_profit', 0.1),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma1 = btind.SMA(self.data.close, period=self.p.maperiod1)
        self.sma2 = btind.SMA(self.data.close, period=self.p.maperiod2)
        self.sma3 = btind.SMA(self.data.close, period=self.p.maperiod3)
        self.rsi = btind.RSI(self.data.close, period=14)
        self.bollinger = btind.BBands(self.data.close, period=self.p.maperiod1, devfactor=2)

        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            # Buy signal: price above all SMAs, RSI oversold, price below bollinger mid
            if (self.dataclose[0] > self.sma1[0] and
                self.dataclose[0] > self.sma2[0] and
                self.dataclose[0] > self.sma3[0] and
                self.rsi[0] < 30):
                self.order = self.buy()
                self.entry_price = self.dataclose[0]
            # Sell signal: price below all SMAs, RSI overbought
            elif (self.dataclose[0] < self.sma1[0] and
                  self.dataclose[0] < self.sma2[0] and
                  self.dataclose[0] < self.sma3[0] and
                  self.rsi[0] > 70):
                self.order = self.sell()
                self.entry_price = self.dataclose[0]
        else:
            # Long position exit
            if self.position.size > 0:
                if self.dataclose[0] >= self.entry_price * (1 + self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] <= self.entry_price * (1 - self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None
            # Short position exit
            elif self.position.size < 0:
                if self.dataclose[0] <= self.entry_price * (1 - self.p.take_profit):
                    self.order = self.close()
                    self.entry_price = None
                elif self.dataclose[0] >= self.entry_price * (1 + self.p.stop_loss):
                    self.order = self.close()
                    self.entry_price = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None
